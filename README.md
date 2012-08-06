KCDDSer
=======

Auto sign in Kingsoft Cloud Disk Drive, sign for points and space award.

金山快盤簽到程式

由 python，webpy，jQuery 開發，工作於SAE。
deploy時請修改：
* config.yaml 及 index.wsgi 的 signall URL
* stmp郵箱發送帳號密碼
* 新版本加入115.com支持，如有舊數據，需要執行:

        update `userer` set user=CONCAT(user,'!kingsoft')
  以更新數據

本軟件集遵循CC-by協議
