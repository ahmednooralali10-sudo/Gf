import requests
from flask import Flask,request,jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
app=Flask(name)
def encode_varint(N):
 H=[]
 while True:
  b=N&0x7F;N>>=7
  if N:b|=0x80
  H.append(b)
  if not N:return bytes(H)
@app.route("/request_clan")
def api_request():
 clan_id=request.args.get("clan_id");uid=request.args.get("uid");pw=request.args.get("pw") or request.args.get("pass")
 if not clan_id:return jsonify({"success":False,"error":"clan_id required"})
 if not uid or not pw:return jsonify({"success":False,"error":"uid and pw required"})
 try:
  r=requests.get(f"http://de26.spaceify.eu:26080/jwt?u={uid}&pw={pw}",timeout=20,verify=False)
  if r.status_code!=200:return jsonify({"success":False,"error":"Login failed"})
  j=r.json()
  if not j.get("jwt"):return jsonify({"success":False,"error":"Login failed"})
  data=j
 except:return jsonify({"success":False,"error":"Login failed"})
 jwt_token=data["jwt"];key_hex=data.get("key","");iv_hex=data.get("iv","")
 if len(key_hex)!=32 or len(iv_hex)!=32:return jsonify({"success":False,"error":"Invalid key/iv from API"})
 key=bytes.fromhex(key_hex);iv=bytes.fromhex(iv_hex)
 try:
  msg=encode_varint((1<<3)|0)+encode_varint(int(clan_id))
  payload=AES.new(key,AES.MODE_CBC,iv).encrypt(pad(msg,16))
  headers={"User-Agent":"Dalvik/2.1.0 (Linux; U; Android 9)","Connection":"Keep-Alive","Accept-Encoding":"gzip","Content-Type":"application/octet-stream","X-Unity-Version":"2018.4.11f1","X-GA":"v1 1","ReleaseVersion":"OB55","Expect":"100-continue","Authorization":f"Bearer {jwt_token}"}
  r=requests.post("https://clientbp.ppmainecoonghj.com/RequestJoinClan",headers=headers,data=payload,verify=False)
  code,text=r.status_code,r.text
 except Exception as e:return jsonify({"success":False,"error":str(e)})
 return jsonify({"success":code==200,"action":"Join Clan","clan_id":clan_id,"account_uid":data.get("account_uid"),"name":data.get("name"),"region":"ME","server_response":text})
app.run(host="0.0.0.0",port=5000)
