#!/usr/bin/env node
/**
 * WhatsApp pair helper — exports QR PNG or pairing code for Zeus relink.
 */
import { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import QRCode from 'qrcode';
import { mkdirSync, writeFileSync, rmSync, existsSync } from 'fs';
import path from 'path';

const SESSION_DIR = process.env.WA_SESSION_DIR || path.join(process.env.HOME, '.hermes', 'whatsapp', 'session');
const OUT_DIR = process.env.WA_QR_OUT_DIR || path.join(process.env.HOME, '.hermes', 'whatsapp', 'relink-current');
const SANDBOX_DIR = process.env.WA_SANDBOX_DIR || '/home/jean/zeus-runtime/delivery-sandbox/public/wa-relink/current';
const TIMEOUT_MS = parseInt(process.env.WA_PAIR_TIMEOUT_MS || `${30 * 60 * 1000}`, 10);
const PAIR_MODE = (process.env.WA_PAIR_MODE || 'qr').toLowerCase();
const PHONE_NUMBER = (process.env.WA_PHONE_NUMBER || '').replace(/\D/g, '');

mkdirSync(SESSION_DIR, { recursive: true });
mkdirSync(OUT_DIR, { recursive: true });
mkdirSync(SANDBOX_DIR, { recursive: true });

const silentLogger = {
  level: 'silent',
  trace() {}, debug() {}, info() {}, warn() {}, error() {}, fatal() {},
  child() { return this; },
};

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
}

function writeStatus(status, extra = {}) {
  const payload = JSON.stringify({ status, mode: PAIR_MODE, updatedAt: new Date().toISOString(), ...extra }, null, 2);
  for (const dir of [OUT_DIR, SANDBOX_DIR]) {
    writeFileSync(path.join(dir, 'status.json'), payload);
  }
}

function writePage({ status, bodyHtml }) {
  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <meta http-equiv="refresh" content="8" />
  <title>Zeus WhatsApp — vincular</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 460px; margin: 2rem auto; padding: 0 1rem; text-align: center; }
    img { width: min(320px, 90vw); height: auto; border: 1px solid #ddd; border-radius: 12px; }
    .code { font-size: 2rem; letter-spacing: 0.35rem; font-weight: 700; margin: 1rem 0; }
    .muted { color: #666; font-size: 0.95rem; line-height: 1.45; }
  </style>
</head>
<body>
  <h1>Vincular WhatsApp a Zeus</h1>
  <p><strong>Estado:</strong> ${status}</p>
  ${bodyHtml}
  <p class="muted">No compartas esta página. Se actualiza sola.</p>
</body>
</html>`;
  for (const dir of [OUT_DIR, SANDBOX_DIR]) {
    writeFileSync(path.join(dir, 'index.html'), html);
  }
}

async function exportQr(qr) {
  const pngBuffer = await QRCode.toBuffer(qr, { type: 'png', width: 320, margin: 2, errorCorrectionLevel: 'M' });
  for (const dir of [OUT_DIR, SANDBOX_DIR]) {
    writeFileSync(path.join(dir, 'qr.png'), pngBuffer);
  }
  writeStatus('waiting_for_scan');
  writePage({
    status: 'Esperando escaneo de QR',
    bodyHtml: `<p class="muted">WhatsApp → Ajustes → Dispositivos vinculados → Vincular un dispositivo</p><p><img src="qr.png?v=${Date.now()}" alt="QR WhatsApp" /></p>`,
  });
  log(`QR PNG exportado en ${path.join(OUT_DIR, 'qr.png')}`);
}

function exportPairingCode(code) {
  activePairingCode = String(code);
  const formatted = activePairingCode.replace(/(.{4})/g, '$1 ').trim();
  for (const dir of [OUT_DIR, SANDBOX_DIR]) {
    writeFileSync(path.join(dir, 'pairing-code.txt'), `${code}\n`);
  }
  writeStatus('waiting_for_code', { pairingCode: formatted });
  writePage({
    status: 'Esperando código en el teléfono',
    bodyHtml: `<p class="muted">En WhatsApp: Dispositivos vinculados → Vincular dispositivo → <strong>Vincular con número de teléfono</strong></p><p class="code">${formatted}</p>`,
  });
  log(`Código de emparejamiento: ${formatted}`);
}

let pairingRequested = false;
let hasConnected = false;
let activePairingCode = '';

function clearSession() {
  if (existsSync(SESSION_DIR)) {
    rmSync(SESSION_DIR, { recursive: true, force: true });
  }
  mkdirSync(SESSION_DIR, { recursive: true });
  pairingRequested = false;
  activePairingCode = '';
}

async function maybeRequestPairingCode(sock, state) {
  if (PAIR_MODE !== 'code' || !PHONE_NUMBER) return;
  if (state.creds.registered || activePairingCode) return;
  if (pairingRequested) return;
  pairingRequested = true;
  try {
    log(`Solicitando código para teléfono terminado en …${PHONE_NUMBER.slice(-4)}`);
    const code = await sock.requestPairingCode(PHONE_NUMBER);
    exportPairingCode(code);
  } catch (err) {
    pairingRequested = false;
    log(`Error solicitando código: ${err}`);
    writeStatus('error', { message: String(err) });
  }
}

async function startSocket() {
  const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);
  const { version } = await fetchLatestBaileysVersion();
  log(`Baileys ${version.join('.')} | mode=${PAIR_MODE} | registered=${state.creds.registered}`);

  const sock = makeWASocket({
    version,
    auth: state,
    logger: silentLogger,
    printQRInTerminal: false,
    browser: ['Hermes Agent', 'Chrome', '120.0'],
    syncFullHistory: false,
    markOnlineOnConnect: false,
    getMessage: async () => ({ conversation: '' }),
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr && PAIR_MODE === 'qr') {
      try {
        await exportQr(qr);
      } catch (err) {
        log(`Error exportando QR: ${err}`);
      }
    }

    if (connection === 'connecting') {
      await maybeRequestPairingCode(sock, state);
    }

    if (connection === 'close') {
      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      log(`Conexión cerrada (reason=${reason})`);

      if (reason === DisconnectReason.loggedOut) {
        if (hasConnected) {
          writeStatus('error', { message: 'logged_out' });
          process.exit(1);
        }
        if (activePairingCode) {
          log('401 durante espera de código — reconectando sin borrar sesión…');
          setTimeout(startSocket, 2000);
          return;
        }
        log('Sesión parcial inválida (401). Limpiando y reintentando…');
        clearSession();
        setTimeout(startSocket, 5000);
        return;
      }

      const delay = reason === 515 ? 1000 : 3000;
      if (reason === 515) {
        log('Reinicio requerido tras emparejamiento (515). Reconectando…');
        writeStatus('reconnecting', { reason: 515 });
      } else {
        writeStatus('reconnecting', { reason });
      }
      setTimeout(startSocket, delay);
    } else if (connection === 'open') {
      hasConnected = true;
      writeStatus('connected');
      writePage({ status: 'Conectado', bodyHtml: '<p class="muted">Emparejamiento completado. Puedes cerrar esta página.</p>' });
      log('WhatsApp conectado. Credenciales guardadas.');
      setTimeout(() => process.exit(0), 2500);
    }
  });
}

writeStatus('starting');
writePage({ status: 'Iniciando…', bodyHtml: '<p class="muted">Generando credenciales de vinculación…</p>' });

setTimeout(() => {
  writeStatus('expired', { message: 'timeout' });
  log('Tiempo de emparejamiento agotado.');
  process.exit(2);
}, TIMEOUT_MS);

startSocket().catch((err) => {
  writeStatus('error', { message: String(err) });
  log(String(err));
  process.exit(1);
});
