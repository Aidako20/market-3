#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

MAIL_TEMPLATE="""Return-Path:<whatever-2a840@postmaster.twitter.com>
To:{to}
cc:{cc}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}
------=_Part_4200734_24778174.1344608186754
Content-Type:text/plain;charset=utf-8
Content-Transfer-Encoding:quoted-printable

Pleasecallmeassoonaspossiblethisafternoon!

--
Sylvie
------=_Part_4200734_24778174.1344608186754
Content-Type:text/html;charset=utf-8
Content-Transfer-Encoding:quoted-printable

<!DOCTYPEhtmlPUBLIC"-//W3C//DTDHTML4.01//EN""http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <metahttp-equiv=3D"Content-Type"content=3D"text/html;charset=3Dutf-8"/>
 </head>=20
 <bodystyle=3D"margin:0;padding:0;background:#ffffff;-webkit-text-size-adjust:100%;">=20

  <p>Pleasecallmeassoonaspossiblethisafternoon!</p>

  <p>--<br/>
     Sylvie
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""

MAIL_TEMPLATE_EXTRA_HTML="""Return-Path:<whatever-2a840@postmaster.twitter.com>
To:{to}
cc:{cc}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}
------=_Part_4200734_24778174.1344608186754
Content-Type:text/plain;charset=utf-8
Content-Transfer-Encoding:quoted-printable

Pleasecallmeassoonaspossiblethisafternoon!

--
Sylvie
------=_Part_4200734_24778174.1344608186754
Content-Type:text/html;charset=utf-8
Content-Transfer-Encoding:quoted-printable

<!DOCTYPEhtmlPUBLIC"-//W3C//DTDHTML4.01//EN""http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <metahttp-equiv=3D"Content-Type"content=3D"text/html;charset=3Dutf-8"/>
 </head>=20
 <bodystyle=3D"margin:0;padding:0;background:#ffffff;-webkit-text-size-adjust:100%;">=20

  <p>Pleasecallmeassoonaspossiblethisafternoon!</p>
  {extra_html}

  <p>--<br/>
     Sylvie
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""


MAIL_TEMPLATE_PLAINTEXT="""Return-Path:<whatever-2a840@postmaster.twitter.com>
To:{to}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:text/plain
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}

Pleasecallmeassoonaspossiblethisafternoon!

--
Sylvie
"""

MAIL_TEMPLATE_HTML="""Return-Path:{return_path}
To:{to}
cc:{cc}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:text/html;charset=utf-8
Content-Transfer-Encoding:quoted-printable
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}

<!DOCTYPEhtmlPUBLIC"-//W3C//DTDHTML4.01//EN""http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <metahttp-equiv=3D"Content-Type"content=3D"text/html;charset=3Dutf-8"/>
 </head>=20
 <bodystyle=3D"margin:0;padding:0;background:#ffffff;-webkit-text-size-adjust:100%;">=20

  <p>Pleasecallmeassoonaspossiblethisafternoon!</p>

  <p>--<br/>
     Sylvie
  <p>
 </body>
</html>
"""

MAIL_MULTIPART_MIXED="""Return-Path:<ignasse.carambar@gmail.com>
X-Original-To:raoul@grosbedon.fr
Delivered-To:raoul@grosbedon.fr
Received:bymail1.grosbedon.com(Postfix,fromuserid10002)
    idE8166BFACA;Fri,23Aug201313:18:01+0200(CEST)
X-Spam-Checker-Version:SpamAssassin3.3.1(2010-03-16)onmail1.grosbedon.com
X-Spam-Level:
X-Spam-Status:No,score=-2.6required=5.0tests=BAYES_00,FREEMAIL_FROM,
    HTML_MESSAGE,RCVD_IN_DNSWL_LOWautolearn=unavailableversion=3.3.1
Received:frommail-ie0-f173.google.com(mail-ie0-f173.google.com[209.85.223.173])
    bymail1.grosbedon.com(Postfix)withESMTPSid9BBD7BFAAA
    for<raoul@openerp.fr>;Fri,23Aug201313:17:55+0200(CEST)
Received:bymail-ie0-f173.google.comwithSMTPidqd12so575130ieb.4
        for<raoul@grosbedon.fr>;Fri,23Aug201304:17:54-0700(PDT)
DKIM-Signature:v=1;a=rsa-sha256;c=relaxed/relaxed;
        d=gmail.com;s=20120113;
        h=mime-version:date:message-id:subject:from:to:content-type;
        bh=dMNHV52EC7GAa7+9a9tqwT9joy9z+1950J/3A6/M/hU=;
        b=DGuv0VjegdSrEe36ADC8XZ9Inrb3Iu+3/52Bm+caltddXFH9yewTr0JkCRQaJgMwG9
         qXTQgP8qu/VFEbCh6scu5ZgU1hknzlNCYr3LT+Ih7dAZVUEHUJdwjzUU1LFV95G2RaCd
         /Lwff6CibuUvrA+0CBO7IRKW0Sn5j0mukYu8dbaKsm6ou6HqS8Nuj85fcXJfHSHp6Y9u
         dmE8jBh3fHCHF/nAvU+8aBNSIzl1FGfiBYb2jCoapIuVFitKR4q5cuoodpkH9XqqtOdH
         DG+YjEyi8L7uvdOfN16eMr7hfUkQei1yQgvGu9/5kXoHg9+Gx6VsZIycn4zoaXTV3Nhn
         nu4g==
MIME-Version:1.0
X-Received:by10.50.124.65withSMTPidmg1mr1144467igb.43.1377256674216;
 Fri,23Aug201304:17:54-0700(PDT)
Received:by10.43.99.71withHTTP;Fri,23Aug201304:17:54-0700(PDT)
Date:Fri,23Aug201313:17:54+0200
Message-ID:<CAP76m_V4BY2F7DWHzwfjteyhW8L2LJswVshtmtVym+LUJ=rASQ@mail.gmail.com>
Subject:Testmailmultipart/mixed
From:=?ISO-8859-1?Q?RaoulGrosbedon=E9e?=<ignasse.carambar@gmail.com>
To:FollowersofASUSTeK-Joseph-Walters<raoul@grosbedon.fr>
Content-Type:multipart/mixed;boundary=089e01536c4ed4d17204e49b8e96

--089e01536c4ed4d17204e49b8e96
Content-Type:multipart/alternative;boundary=089e01536c4ed4d16d04e49b8e94

--089e01536c4ed4d16d04e49b8e94
Content-Type:text/plain;charset=ISO-8859-1

Shouldcreateamultipart/mixed:fromgmail,*bold*,withattachment.

--
MarcelBoitempoils.

--089e01536c4ed4d16d04e49b8e94
Content-Type:text/html;charset=ISO-8859-1

<divdir="ltr">Shouldcreateamultipart/mixed:fromgmail,<b>bold</b>,withattachment.<brclear="all"><div><br></div>--<br>MarcelBoitempoils.</div>

--089e01536c4ed4d16d04e49b8e94--
--089e01536c4ed4d17204e49b8e96
Content-Type:text/plain;charset=US-ASCII;name="test.txt"
Content-Disposition:attachment;filename="test.txt"
Content-Transfer-Encoding:base64
X-Attachment-Id:f_hkpb27k00

dGVzdAo=
--089e01536c4ed4d17204e49b8e96--"""

MAIL_MULTIPART_MIXED_TWO="""X-Original-To:raoul@grosbedon.fr
Delivered-To:raoul@grosbedon.fr
Received:bymail1.grosbedon.com(Postfix,fromuserid10002)
    idE8166BFACA;Fri,23Aug201313:18:01+0200(CEST)
From:"BruceWayne"<bruce@wayneenterprises.com>
Content-Type:multipart/alternative;
 boundary="Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227"
Message-Id:<6BB1FAB2-2104-438E-9447-07AE2C8C4A92@sexample.com>
Mime-Version:1.0(MacOSXMail7.3\(1878.6\))

--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227
Content-Transfer-Encoding:7bit
Content-Type:text/plain;
    charset=us-ascii

Firstandsecondpart

--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227
Content-Type:multipart/mixed;
 boundary="Apple-Mail=_CA6C687E-6AA0-411E-B0FE-F0ABB4CFED1F"

--Apple-Mail=_CA6C687E-6AA0-411E-B0FE-F0ABB4CFED1F
Content-Transfer-Encoding:7bit
Content-Type:text/html;
    charset=us-ascii

<html><head></head><body>Firstpart</body></html>

--Apple-Mail=_CA6C687E-6AA0-411E-B0FE-F0ABB4CFED1F
Content-Disposition:inline;
    filename=thetruth.pdf
Content-Type:application/pdf;
    name="thetruth.pdf"
Content-Transfer-Encoding:base64

SSBhbSB0aGUgQmF0TWFuCg==

--Apple-Mail=_CA6C687E-6AA0-411E-B0FE-F0ABB4CFED1F
Content-Transfer-Encoding:7bit
Content-Type:text/html;
    charset=us-ascii

<html><head></head><body>Secondpart</body></html>
--Apple-Mail=_CA6C687E-6AA0-411E-B0FE-F0ABB4CFED1F--

--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227--
"""

MAIL_FILE_ENCODING="""MIME-Version:1.0
Date:Sun,26Mar202305:23:22+0200
Message-ID:{msg_id}
Subject:{subject}
From:"SylvieLelitre"<test.sylvie.lelitre@agrolait.com>
To:groups@test.com
Content-Type:multipart/mixed;boundary="000000000000b951de05f7c47a9e"

--000000000000b951de05f7c47a9e
Content-Type:multipart/alternative;boundary="000000000000b951da05f7c47a9c"

--000000000000b951da05f7c47a9c
Content-Type:text/plain;charset="UTF-8"

TestBody

--000000000000b951da05f7c47a9c
Content-Type:text/html;charset="UTF-8"

<divdir="ltr">TestBody</div>

--000000000000b951da05f7c47a9c--
--000000000000b951de05f7c47a9e
Content-Type:text/plain;name="test.txt"{charset}
Content-Disposition:attachment;filename="test.txt"
Content-Transfer-Encoding:base64
X-Attachment-Id:f_lfosfm0l0
Content-ID:<f_lfosfm0l0>

{content}

--000000000000b951de05f7c47a9e--
"""

MAIL_MULTIPART_BINARY_OCTET_STREAM="""X-Original-To:raoul@grosbedon.fr
Delivered-To:raoul@grosbedon.fr
Received:bymail1.grosbedon.com(Postfix,fromuserid10002)
    idE8166BFACA;Fri,10Nov202106:04:01+0200(CEST)
From:"BruceWayne"<bruce@wayneenterprises.com>
Content-Type:multipart/alternative;
 boundary="Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227"
Message-Id:<6BB1FAB2-2104-438E-9447-07AE2C8C4A92@sexample.com>
Mime-Version:1.0(MacOSXMail7.3\\(1878.6\\))

--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227
Content-Transfer-Encoding:7bit
Content-Type:text/plain;
    charset=us-ascii

Theattachedfilecontainsb"Helloworld\\n"

--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227
Content-Disposition:attachment;
 filename="hello_world.dat"
Content-Type:binary/octet-stream;
 name="hello_world.dat"
Content-Transfer-Encoding:base64

SGVsbG8gd29ybGQK
--Apple-Mail=_9331E12B-8BD2-4EC7-B53E-01F3FBEC9227--
"""

MAIL_MULTIPART_INVALID_ENCODING="""Return-Path:<whatever-2a840@postmaster.twitter.com>
To:{to}
cc:{cc}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:multipart/alternative;
    boundary="00000000000005d9da05fa394cc0"
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}

--00000000000005d9da05fa394cc0
Content-Type:multipart/alternative;boundary="00000000000005d9d905fa394cbe"

--00000000000005d9d905fa394cbe
Content-Type:text/plain;charset="UTF-8"

Dearcustomer,

PleasefindattachedthePeppolBis3attachmentofyourinvoice(withan
encodingerrorintheaddress)

Cheers,

--00000000000005d9d905fa394cbe
Content-Type:text/html;charset="UTF-8"

<divdir="ltr">Dearcustomer,<div><br></div><div>PleasefindattachedthePeppolBis3attachmentofyourinvoice(withanencodingerrorintheaddress)</div><div><br></div><div>Cheers,</div></div>

--00000000000005d9d905fa394cbe--

--00000000000005d9da05fa394cc0
Content-Type:text/xml;charset="US-ASCII";
 name="bis3_with_error_encoding_address.xml"
Content-Disposition:attachment;
	filename="bis3_with_error_encoding_address.xml"
Content-Transfer-Encoding:base64
Content-ID:<f_lgxgdqx40>
X-Attachment-Id:f_lgxgdqx40

PEludm9pY2UgeG1sbnM6Y2JjPSJ1cm46b2FzaXM6bmFtZXM6c3BlY2lmaWNhdGlvbjp1Ymw6c2No
ZW1hOnhzZDpDb21tb25CYXNpY0NvbXBvbmVudHMtMiIgeG1sbnM9InVybjpvYXNpczpuYW1lczpz
cGVjaWZpY2F0aW9uOnVibDpzY2hlbWE6eHNkOkludm9pY2UtMiI+DQo8Y2JjOlN0cmVldE5hbWU+
Q2hhdXNz77+977+9ZSBkZSBCcnV4ZWxsZXM8L2NiYzpTdHJlZXROYW1lPg0KPC9JbnZvaWNlPg0K
--00000000000005d9da05fa394cc0--
"""

MAIL_MULTIPART_OMITTED_CHARSET="""Return-Path:<whatever-2a840@postmaster.twitter.com>
To:{to}
cc:{cc}
Received:bymail1.openerp.com(Postfix,fromuserid10002)
    id5DF9ABFB2A;Fri,10Aug201216:16:39+0200(CEST)
From:{email_from}
Subject:{subject}
MIME-Version:1.0
Content-Type:multipart/alternative;
    boundary="00000000000005d9da05fa394cc0"
Date:Fri,10Aug201214:16:26+0000
Message-ID:{msg_id}
{extra}

--00000000000005d9da05fa394cc0
Content-Type:multipart/alternative;boundary="00000000000005d9d905fa394cbe"

--00000000000005d9d905fa394cbe
Content-Type:text/plain;charset="UTF-8"

Dearcustomer,

PleasefindattachedtheUBLattachmentofyourinvoice

Cheers,

--00000000000005d9d905fa394cbe
Content-Type:text/html;charset="UTF-8"

<divdir="ltr">Dearcustomer,<div><br></div><div>PleasefindattachedtheUBLattachmentofyourinvoice</div><div><br></div><div>Cheers,</div></div>

--00000000000005d9d905fa394cbe--

--00000000000005d9da05fa394cc0
Content-Disposition:attachment;filename="bis3.xml"
Content-Transfer-Encoding:base64
Content-Type:text/xml;name="bis3.xml"
Content-ID:<f_lgxgdqx40>
X-Attachment-Id:f_lgxgdqx40

PEludm9pY2U+Q2hhdXNzw6llIGRlIEJydXhlbGxlczwvSW52b2ljZT4=
--00000000000005d9da05fa394cc0--
"""


MAIL_SINGLE_BINARY="""X-Original-To:raoul@grosbedon.fr
Delivered-To:raoul@grosbedon.fr
Received:bymail1.grosbedon.com(Postfix,fromuserid10002)
    idE8166BFACA;Fri,23Aug201313:18:01+0200(CEST)
From:"BruceWayne"<bruce@wayneenterprises.com>
Content-Type:application/pdf;
Content-Disposition:filename=thetruth.pdf
Content-Transfer-Encoding:base64
Message-Id:<6BB1FAB2-2104-438E-9447-07AE2C8C4A92@sexample.com>
Mime-Version:1.0(MacOSXMail7.3\(1878.6\))

SSBhbSB0aGUgQmF0TWFuCg=="""


MAIL_MULTIPART_WEIRD_FILENAME="""X-Original-To:john@doe.com
Delivered-To:johndoe@example.com
Received:bymail.example.com(Postfix,fromuserid10002)
    idE8166BFACB;Fri,23Aug201313:18:02+0200(CEST)
From:"BruceWayne"<bruce@wayneenterprises.com>
Subject:test
Message-ID:<c0c20fdd-a38e-b296-865b-d9232bf30ce5@flectrahq.com>
Date:Mon,26Aug201916:55:09+0200
MIME-Version:1.0
Content-Type:multipart/mixed;
 boundary="------------FACA7766210AAA981EAE01F3"
Content-Language:en-US

Thisisamulti-partmessageinMIMEformat.
--------------FACA7766210AAA981EAE01F3
Content-Type:text/plain;charset=utf-8;format=flowed
Content-Transfer-Encoding:7bit

plop


--------------FACA7766210AAA981EAE01F3
Content-Type:text/plain;charset=UTF-8;
 name="=?UTF-8?B?NjJfQDssXVspPS4ow4fDgMOJLnR4dA==?="
Content-Transfer-Encoding:base64
Content-Disposition:attachment;
 filename*0*=utf-8'en-us'%36%32%5F%40%3B%2C%5D%5B%29%3D%2E%28%C3%87%C3%80%C3%89;
 filename*1*=%2E%74%78%74

SSBhbSBhIGZpbGUgd2l0aCBhIHZhbGlkIHdpbmRvd3MgZmlsZW5hbWUK
--------------FACA7766210AAA981EAE01F3--
"""


MAIL_MULTIPART_IMAGE="""X-Original-To:raoul@example.com
Delivered-To:micheline@example.com
Received:bymail1.example.com(Postfix,fromuserid99999)
    id9DFB7BF509;Thu,17Dec201515:22:56+0100(CET)
X-Spam-Checker-Version:SpamAssassin3.4.0(2014-02-07)onmail1.example.com
X-Spam-Level:*
X-Spam-Status:No,score=1.1required=5.0tests=FREEMAIL_FROM,
    HTML_IMAGE_ONLY_08,HTML_MESSAGE,RCVD_IN_DNSWL_LOW,RCVD_IN_MSPIKE_H3,
    RCVD_IN_MSPIKE_WL,T_DKIM_INVALIDautolearn=noautolearn_force=noversion=3.4.0
Received:frommail-lf0-f44.example.com(mail-lf0-f44.example.com[209.85.215.44])
    bymail1.example.com(Postfix)withESMTPSid1D80DBF509
    for<micheline@example.com>;Thu,17Dec201515:22:56+0100(CET)
Authentication-Results:mail1.example.com;dkim=pass
    reason="2048-bitkey;unprotectedkey"
    header.d=example.comheader.i=@example.comheader.b=kUkTIIlt;
    dkim-adsp=pass;dkim-atps=neutral
Received:bymail-lf0-f44.example.comwithSMTPidz124so47959461lfa.3
        for<micheline@example.com>;Thu,17Dec201506:22:56-0800(PST)
DKIM-Signature:v=1;a=rsa-sha256;c=relaxed/relaxed;
        d=example.com;s=20120113;
        h=mime-version:date:message-id:subject:from:to:content-type;
        bh=GdrEuMrz6vxo/Z/F+mJVho/1wSe6hbxLx2SsP8tihzw=;
        b=kUkTIIlt6fe4dftKHPNBkdHU2rO052o684R0e2bqH7roGUQFb78scYE+kqX0wo1zlk
         zhKPVBR1TqTsYlqcHu+D3aUzai7L/Q5m40sSGn7uYGkZJ6m1TwrWNqVIgTZibarqvy94
         NWhrjjK9gqd8segQdSjCgTipNSZME4bJCzPyBg/D5mqe07FPBJBGoF9SmIzEBhYeqLj1
         GrXjb/D8J11aOyzmVvyt+bT+oeLUJI8E7qO5g2eQkMncyu+TyIXaRofOOBA14NhQ+0nS
         w5O9rzzqkKuJEG4U2TJ2Vi2nl2tHJW2QPfTtFgcCzGxQ0+5n88OVlbGTLnhEIJ/SYpem
         O5EA==
MIME-Version:1.0
X-Received:by10.25.167.197withSMTPidq188mr22222517lfe.129.1450362175493;
 Thu,17Dec201506:22:55-0800(PST)
Received:by10.25.209.145withHTTP;Thu,17Dec201506:22:55-0800(PST)
Date:Thu,17Dec201515:22:55+0100
Message-ID:<CAP76m_UB=aLqWEFccnq86AhkpwRB3aZoGL9vMffX7co3YEro_A@mail.gmail.com>
Subject:{subject}
From:=?UTF-8?Q?Thibault_Delavall=C3=A9e?=<raoul@example.com>
To:{to}
Content-Type:multipart/related;boundary=001a11416b9e9b229a05272b7052

--001a11416b9e9b229a05272b7052
Content-Type:multipart/alternative;boundary=001a11416b9e9b229805272b7051

--001a11416b9e9b229805272b7051
Content-Type:text/plain;charset=UTF-8
Content-Transfer-Encoding:quoted-printable

Premi=C3=A8reimage,orang=C3=A9e.

[image:Inlineimage1]

Secondeimage,rosa=C3=A7=C3=A9e.

[image:Inlineimage2]

Troisi=C3=A8meimage,verte!=C2=B5

[image:Inlineimage3]

J'esp=C3=A8requetoutsepasserabien.
--=20
ThibaultDelavall=C3=A9e

--001a11416b9e9b229805272b7051
Content-Type:text/html;charset=UTF-8
Content-Transfer-Encoding:quoted-printable

<divdir=3D"ltr"><div>Premi=C3=A8reimage,orang=C3=A9e.</div><div><br></di=
v><div><imgsrc=3D"cid:ii_151b519fc025fdd3"alt=3D"Inlineimage1"width=3D=
"2"height=3D"2"><br></div><div><br></div><div>Secondeimage,rosa=C3=A7=C3=
=A9e.</div><div><br></div><div><imgsrc=3D"cid:ii_151b51a290ed6a91"alt=3D"=
Inlineimage2"width=3D"2"height=3D"2"></div><div><br></div><div>Troisi=
=C3=A8meimage,verte!=C2=B5</div><div><br></div><div><imgsrc=3D"cid:ii_15=
1b51a37e5eb7a6"alt=3D"Inlineimage3"width=3D"10"height=3D"10"><br></div=
><div><br></div><div>J&#39;esp=C3=A8requetoutsepasserabien.</div>--<b=
r><divclass=3D"gmail_signature">ThibaultDelavall=C3=A9e</div>
</div>

--001a11416b9e9b229805272b7051--
--001a11416b9e9b229a05272b7052
Content-Type:image/gif;name="=?UTF-8?B?b3JhbmfDqWUuZ2lm?="
Content-Disposition:inline;filename="=?UTF-8?B?b3JhbmfDqWUuZ2lm?="
Content-Transfer-Encoding:base64
Content-ID:<ii_151b519fc025fdd3>
X-Attachment-Id:ii_151b519fc025fdd3

R0lGODdhAgACALMAAAAAAP///wAAAP//AP8AAP+AAAD/AAAAAAAA//8A/wAAAAAAAAAAAAAAAAAA
AAAAACwAAAAAAgACAAAEA7DIEgA7
--001a11416b9e9b229a05272b7052
Content-Type:image/gif;name="=?UTF-8?B?dmVydGUhwrUuZ2lm?="
Content-Disposition:inline;filename="=?UTF-8?B?dmVydGUhwrUuZ2lm?="
Content-Transfer-Encoding:base64
Content-ID:<ii_151b51a37e5eb7a6>
X-Attachment-Id:ii_151b51a37e5eb7a6

R0lGODlhCgAKALMAAAAAAIAAAACAAICAAAAAgIAAgACAgMDAwICAgP8AAAD/AP//AAAA//8A/wD/
/////ywAAAAACgAKAAAEClDJSau9OOvNe44AOw==
--001a11416b9e9b229a05272b7052
Content-Type:image/gif;name="=?UTF-8?B?cm9zYcOnw6llLmdpZg==?="
Content-Disposition:inline;filename="=?UTF-8?B?cm9zYcOnw6llLmdpZg==?="
Content-Transfer-Encoding:base64
Content-ID:<ii_151b51a290ed6a91>
X-Attachment-Id:ii_151b51a290ed6a91

R0lGODdhAgACALMAAAAAAP///wAAAP//AP8AAP+AAAD/AAAAAAAA//8A/wAAAP+AgAAAAAAAAAAA
AAAAACwAAAAAAgACAAAEA3DJFQA7
--001a11416b9e9b229a05272b7052--
"""

MAIL_EML_ATTACHMENT="""Subject:Re:testattac
From:{email_from}
To:{to}
References:<f3b9f8f8-28fa-2543-cab2-7aa68f679ebb@flectrahq.com>
Message-ID:<cb7eaf62-58dc-2017-148c-305d0c78892f@flectrahq.com>
Date:Wed,14Mar201814:26:58+0100
User-Agent:Mozilla/5.0(X11;Linuxx86_64;rv:52.0)Gecko/20100101
 Thunderbird/52.6.0
MIME-Version:1.0
In-Reply-To:<f3b9f8f8-28fa-2543-cab2-7aa68f679ebb@flectrahq.com>
Content-Type:multipart/mixed;
 boundary="------------A6B5FD5F68F4D73ECD739009"
Content-Language:en-US

Thisisamulti-partmessageinMIMEformat.
--------------A6B5FD5F68F4D73ECD739009
Content-Type:text/plain;charset=utf-8;format=flowed
Content-Transfer-Encoding:7bit



On14/03/1814:20,Anonwrote:
>Somenicecontent
>


--------------A6B5FD5F68F4D73ECD739009
Content-Type:message/rfc822;
 name="original_msg.eml"
Content-Transfer-Encoding:8bit
Content-Disposition:attachment;
 filename="original_msg.eml"

Delivered-To:anon2@gmail1.openerp.com
Received:by10.46.1.170withSMTPidf42csp2379722lji;
        Mon,5Mar201801:19:23-0800(PST)
X-Google-Smtp-Source:AG47ELsYTlAcblMxfnaEENQuF+MFoac5Q07wieyw0cybq/qOX4+DmayqoQILkiWT+NiTOcnr/ACO
X-Received:by10.28.154.213withSMTPidc204mr7237750wme.64.1520241563503;
        Mon,05Mar201801:19:23-0800(PST)
ARC-Seal:i=1;a=rsa-sha256;t=1520241563;cv=none;
        d=google.com;s=arc-20160816;
        b=BqgMSbqmbpYW1ZtfGTVjj/654MBmabw4XadNZEaI96hDaub6N6cP8Guu3PoxscI9os
         0OLYVP1s/B+Vv9rIzulCwHyHsgnX+aTxGYepTDN6x8SA9Qeb9aQoNSVvQLryTAoGpaFr
         vXhw8aPWyr28edE03TDFA/s7X65Bf6dV5zJdMiUPVqGkfYfcTHMf3nDER5vk8vQj7tve
         Cfyy0h9vLU9RSEtdFwmlEkLmgT9NQ3GDf0jQ97eMXPgR2q6duCPoMcz15KlWOno53xgH
         EiV7aIZ5ZMN/m+/2xt3br/ubJ5euFojWhDnHUZoaqd08TCSQPd4fFCCx75MjDeCnwYMn
         iKSg==
ARC-Message-Signature:i=1;a=rsa-sha256;c=relaxed/relaxed;d=google.com;s=arc-20160816;
        h=content-language:mime-version:user-agent:date:message-id:subject
         :from:to:dkim-signature:arc-authentication-results;
        bh=/UIFqhjCCbwBLsI4w7YY98QH6G/wxe+2W4bbMDCskjM=;
        b=Wv5jt+usnSgWI96GaZWUN8/VKl1drueDpU/4gkyX/iK4d6S4CuSDjwYAc3guz/TjeW
         GoKCqT30IGZoStpXQbuLry7ezXNK+Fp8MJKN2n/x5ClJWHxIsxIGlP2QC3TO8RI0P5o0
         GXG9izW93q1ubkdPJFt3unSjjwSYf5XVQAZQtRm9xKjqA+lbtFbsnbjJ4wgYBURnD8ma
         Qxb2xsxXDelaZvtdlzHRDn5SEkbqhcCclEYw6oRLpVQFZeYtPxcCleVybtj2owJxdaLp
         7wXuo/gpYe6E2cPuS2opei8AzjEhYTNzlYXTPvaoxCCTTjfGTaPv22TeRDehuIXngSEl
         Nmmw==
ARC-Authentication-Results:i=1;mx.google.com;
       dkim=passheader.i=@flectrahq.comheader.s=mailheader.b=MCzhjB9b;
       spf=pass(google.com:domainofsoup@flectrahq.comdesignates149.202.180.44aspermittedsender)smtp.mailfrom=soup@flectrahq.com;
       dmarc=pass(p=NONEsp=NONEdis=NONE)header.from=flectrahq.com
Return-Path:<soup@flectrahq.com>
Received:frommail2.flectrahq.com(mail2.flectrahq.com.[149.202.180.44])
        bymx.google.comwithESMTPSidy4si4279200wmy.148.2018.03.05.01.19.22
        (version=TLS1_2cipher=ECDHE-RSA-AES128-GCM-SHA256bits=128/128);
        Mon,05Mar201801:19:23-0800(PST)
Received-SPF:pass(google.com:domainofsoup@flectrahq.comdesignates149.202.180.44aspermittedsender)client-ip=149.202.180.44;
Authentication-Results:mx.google.com;
       dkim=passheader.i=@flectrahq.comheader.s=mailheader.b=MCzhjB9b;
       spf=pass(google.com:domainofsoup@flectrahq.comdesignates149.202.180.44aspermittedsender)smtp.mailfrom=soup@flectrahq.com;
       dmarc=pass(p=NONEsp=NONEdis=NONE)header.from=flectrahq.com
Received:from[10.10.31.24](unknown[91.183.114.50])
	(Authenticatedsender:soup)
	bymail2.flectrahq.com(Postfix)withESMTPSAid7B571A4085
	for<what@flectrahq.com>;Mon, 5Mar201810:19:21+0100(CET)
DKIM-Signature:v=1;a=rsa-sha256;c=simple/simple;d=flectrahq.com;s=mail;
	t=1520241562;bh=L2r7Sp/vjogIdM1k8H9zDGDjnhKolsTTLLjndnFC4Jc=;
	h=To:From:Subject:Date:From;
	b=MCzhjB9bnsrJ3uKjq+GjujFxmtrq3fc7Vv7Vg2C72EPKnkxgqy6yPjWKtXbBlaiT3
	YjKI24aiSQlOeOPQiqFgiDzeqqemNDp+CRuhoYz1Vbz+ESRaHtkWRLb7ZjvohS2k7e
	RTq7tUxY2nUL2YrNHV7DFYtJVBwiTuyLP6eAiJdE=
To:what@flectrahq.com
From:Soup<soup@flectrahq.com>
Subject:=?UTF-8?Q?Soupe_du_jour_:_Pois_cass=c3=a9s?=
Message-ID:<a05d8334-7b7c-df68-c96a-4a88ed19f31b@flectrahq.com>
Date:Mon,5Mar201810:19:21+0100
User-Agent:Mozilla/5.0(X11;Linuxx86_64;rv:52.0)Gecko/20100101
 Thunderbird/52.6.0
MIME-Version:1.0
Content-Type:multipart/alternative;
 boundary="------------1F2D18B1129FC2F0B9EECF50"
Content-Language:en-US
X-Spam-Status:No,score=-1.2required=5.0tests=ALL_TRUSTED,BAYES_00,
	HTML_IMAGE_ONLY_08,HTML_MESSAGE,T_REMOTE_IMAGEautolearn=no
	autolearn_force=noversion=3.4.0
X-Spam-Checker-Version:SpamAssassin3.4.0(2014-02-07)onmail2.flectrahq.com

Thisisamulti-partmessageinMIMEformat.
--------------1F2D18B1129FC2F0B9EECF50
Content-Type:text/plain;charset=utf-8;format=flowed
Content-Transfer-Encoding:8bit

Résultatderecherched'imagespour"dessinlaprincesseaupetitpois"

--
Soup

FlectraS.A.
ChausséedeNamur,40
B-1367GrandRosière
Web:http://www.flectrahq.com


--------------1F2D18B1129FC2F0B9EECF50
Content-Type:text/html;charset=utf-8
Content-Transfer-Encoding:8bit

<html>
  <head>

    <metahttp-equiv="content-type"content="text/html;charset=utf-8">
  </head>
  <bodytext="#000000"bgcolor="#FFFFFF">
    <p><img
src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQjCNAadd3NDM8g9w0P_-gAVYrrqC0wmBNYKGsTZ2Pst5SsNxTRnA"
        alt="Résultatderecherched'imagespour&quot;dessinla
        princesseaupetitpois&quot;"></p>
    <preclass="moz-signature"cols="72">--
Soup

FlectraS.A.
ChausséedeNamur,40
B-1367GrandRosière
Web:<aclass="moz-txt-link-freetext"href="http://www.flectrahq.com">http://www.flectrahq.com</a></pre>
  </body>
</html>

--------------1F2D18B1129FC2F0B9EECF50--

--------------A6B5FD5F68F4D73ECD739009--"""

MAIL_EML_ATTACHMENT_BOUNCE_HEADERS="""\
Date:Tue,24Dec201911:32:07+0100(CET)
MIME-Version:1.0
Content-Type:multipart/mixed;boundary=16063919151.b32bE0eD.7
Content-Transfer-Encoding:7bit
Subject:UndeliveredMailReturnedtoSender
From:{email_from}
To:{to}
Message-Id:<20191224103207.415713014C@example.com>
Return-Path:<MAILER-DAEMON>
Delivered-To:flectra+82240-account.invoice-19177@mycompany.example.com
Received:byexample.com(Postfix)id415713014C;Tue,24Dec
 201911:32:07+0100(CET)
Auto-Submitted:auto-replied


--16063919151.b32bE0eD.7
MIME-Version:1.0
Content-Type:multipart/alternative;boundary=16063919150.2cD3F37.7
Content-Transfer-Encoding:7bit
Content-ID:<16063919152.fD96.7@8f286b7b7880>


--16063919150.2cD3F37.7
Content-Type:text/plain;charset=US-ASCII
Content-Disposition:inline
Content-Transfer-Encoding:8bit

Thisisthemailsystemathostexample.com.

I'msorrytohavetoinformyouthatyourmessagecouldnot
bedeliveredtooneormorerecipients.It'sattachedbelow.

Forfurtherassistance,pleasesendmailtopostmaster.

Ifyoudoso,pleaseincludethisproblemreport.Youcan
deleteyourowntextfromtheattachedreturnedmessage.


--16063919151.b32bE0eD.7
Content-Type:text/rfc822-headers
Content-Transfer-Encoding:7bit

Return-Path:<bounce+82240-account.invoice-19177@mycompany.example.com>
Received:byexample.com(Postfix)id415713014C;Tue,24Dec
Content-Type:multipart/mixed;boundary="===============3600759226158551994=="
MIME-Version:1.0
Message-Id:{msg_id}
references:<1571814481.189281940460205.799582441238467-openerp-19177-account.invoice@mycompany.example.com>
Subject:Test
From:"Test"<noreply+srglvrz-gmail.com@mycompany.example.com>
Reply-To:"MYCOMPANY"<info@mycompany.example.com>
To:"Test"<test@anothercompany.example.com>
Date:Tue,24Dec201910:32:05-0000
X-Flectra-Objects:account.invoice-19177

--16063919151.b32bE0eD.7--"""

MAIL_XHTML="""Return-Path:<xxxx@xxxx.com>
Received:fromxxxx.internal(xxxx.xxxx.internal[1.1.1.1])
	byxxxx(xxxx1.1.1-111-g972eecc-slipenbois)withLMTPA;
	Fri,13Apr201822:11:52-0400
X-Cyrus-Session-Id:sloti35d1t38-1111111-11111111111-5-11111111111111111111
X-Sieve:CMUSieve1.0
X-Spam-known-sender:no("EmailfailedDMARCpolicyfordomain");in-addressbook
X-Spam-score:0.0
X-Spam-hits:ALL_TRUSTED-1,BAYES_00-1.9,FREEMAIL_FROM0.001,
  HTML_FONT_LOW_CONTRAST0.001,HTML_MESSAGE0.001,SPF_SOFTFAIL0.665,
  LANGUAGESen,BAYES_USEDglobal,SA_VERSION1.1.0
X-Spam-source:IP='1.1.1.1',Host='unk',Country='unk',FromHeader='com',
  MailFrom='com'
X-Spam-charsets:plain='utf-8',html='utf-8'
X-IgnoreVacation:yes("EmailfailedDMARCpolicyfordomain")
X-Resolved-to:catchall@xxxx.xxxx
X-Delivered-to:catchall@xxxx.xxxx
X-Mail-from:xxxx@xxxx.com
Received:frommx4([1.1.1.1])
  byxxxx.internal(LMTPProxy);Fri,13Apr201822:11:52-0400
Received:fromxxxx.xxxx.com(localhost[127.0.0.1])
	byxxxx.xxxx.internal(Postfix)withESMTPidE1111C1111;
	Fri,13Apr201822:11:51-0400(EDT)
Received:fromxxxx.xxxx.internal(localhost[127.0.0.1])
    byxxxx.xxxx.com(AuthenticationMilter)withESMTP
    idBBDD1111D1A;
    Fri,13Apr201822:11:51-0400
ARC-Authentication-Results:i=1;xxxx.xxxx.com;arc=none(nosignaturesfound);
    dkim=pass(2048-bitrsakeysha256)header.d=xxxx.comheader.i=@xxxx.comheader.b=P1aaAAaax-bits=2048x-keytype=rsax-algorithm=sha256x-selector=fm2;
    dmarc=fail(p=none,d=none)header.from=xxxx.com;
    iprev=passpolicy.iprev=1.1.1.1(out1-smtp.xxxx.com);
    spf=softfailsmtp.mailfrom=xxxx@xxxx.comsmtp.helo=out1-smtp.xxxx.com;
    x-aligned-from=pass(Addressmatch);
    x-cm=nonescore=0;
    x-ptr=passx-ptr-helo=out1-smtp.xxxx.comx-ptr-lookup=out1-smtp.xxxx.com;
    x-return-mx=passsmtp.domain=xxxx.comsmtp.result=passsmtp_is_org_domain=yesheader.domain=xxxx.comheader.result=passheader_is_org_domain=yes;
    x-tls=passversion=TLSv1.2cipher=ECDHE-RSA-AES128-GCM-SHA256bits=128/128;
    x-vs=cleanscore=0state=0
Authentication-Results:xxxx.xxxx.com;
    arc=none(nosignaturesfound);
    dkim=pass(2048-bitrsakeysha256)header.d=xxxx.comheader.i=@xxxx.comheader.b=P1awJPiyx-bits=2048x-keytype=rsax-algorithm=sha256x-selector=fm2;
    dmarc=fail(p=none,d=none)header.from=xxxx.com;
    iprev=passpolicy.iprev=66.111.4.25(out1-smtp.xxxx.com);
    spf=softfailsmtp.mailfrom=xxxx@xxxx.comsmtp.helo=out1-smtp.xxxx.com;
    x-aligned-from=pass(Addressmatch);
    x-cm=nonescore=0;
    x-ptr=passx-ptr-helo=out1-smtp.xxxx.comx-ptr-lookup=out1-smtp.xxxx.com;
    x-return-mx=passsmtp.domain=xxxx.comsmtp.result=passsmtp_is_org_domain=yesheader.domain=xxxx.comheader.result=passheader_is_org_domain=yes;
    x-tls=passversion=TLSv1.2cipher=ECDHE-RSA-AES128-GCM-SHA256bits=128/128;
    x-vs=cleanscore=0state=0
X-ME-VSCategory:clean
X-ME-CMScore:0
X-ME-CMCategory:none
Received-SPF:softfail
    (gmail.com..._spf.xxxx.com:Senderisnotauthorizedbydefaulttouse'xxxx@xxxx.com'in'mfrom'identity,howeverdomainisnotcurrentlypreparedforfalsefailures(mechanism'~all'matched))
    receiver=xxxx.xxxx.com;
    identity=mailfrom;
    envelope-from="xxxx@xxxx.com";
    helo=out1-smtp.xxxx.com;
    client-ip=1.1.1.1
Received:fromxxxx.xxxx.internal(gateway1.xxxx.internal[1.1.1.1])
	(usingTLSv1.2withcipherECDHE-RSA-AES128-GCM-SHA256(128/128bits))
	(Noclientcertificaterequested)
	byxxxx.xxxx.internal(Postfix)withESMTPS;
	Fri,13Apr201822:11:51-0400(EDT)
Received:fromcompute3.internal(xxxx.xxxx.internal[10.202.2.43])
	byxxxx.xxxx.internal(Postfix)withESMTPid8BD5B21BBD;
	Fri,13Apr201822:11:51-0400(EDT)
Received:fromxxxx([10.202.2.163])
  byxxxx.internal(MEProxy);Fri,13Apr201822:11:51-0400
X-ME-Sender:<xms:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa>
Received:from[1.1.1.1](unknown[1.1.1.1])
	bymail.xxxx.com(Postfix)withESMTPAidBF5E1111D
	for<catchall@xxxx.xxxx>;Fri,13Apr201822:11:50-0400(EDT)
From:SylvieLelitre<test.sylvie.lelitre@agrolait.com>
To:generic@mydomain.com
Subject:Re:xxxx(RefPO1)
Date:Sat,14Apr201802:11:42+0000
Message-Id:<em67f5c44a-xxxx-xxxx-xxxx-69f56d618a94@wswin7hg4n4l1ce>
In-Reply-To:<829228111124527.1111111602.256611118262939-openerp-129-xxxx.xxxx@ip-1-1-1-1>
References:<867911111953277.1523671337.187951111160400-openerp-129-xxxx.xxxx@ip-1-1-1-1>
 <867911111953277.1523671337.256611118262939-openerp-129-xxxx.xxxx@ip-1-1-1-1>
Reply-To:"xxxxxxxx"<xxxx@xxxx.com>
User-Agent:eM_Client/7.0.26687.0
Mime-Version:1.0
Content-Type:multipart/alternative;
 boundary="------=_MB48E455BD-1111-42EC-1111-886CDF48905E"

--------=_MB48E455BD-1111-42EC-1111-886CDF48905E
Content-Type:text/plain;format=flowed;charset=utf-8
Content-Transfer-Encoding:quoted-printable

xxxx


------OriginalMessage------
From:"xxxx"<xxxx@xxxx.com>
To:"xxxx"<xxxx@xxxx.com>
Sent:4/13/20187:06:43PM
Subject:xxxx

>xxxx

--------=_MB48E455BD-1111-42EC-1111-886CDF48905E
Content-Type:text/html;charset=utf-8
Content-Transfer-Encoding:quoted-printable

<?xmlversion=3D"1.0"encoding=3D"utf-16"?><html><head><styletype=3D"text/=
css"><!--blockquote.cite
{margin-left:5px;margin-right:0px;padding-left:10px;padding-right:=
 0px;border-left-width:1px;border-left-style:solid;border-left-color:=
 rgb(204,204,204);}
blockquote.cite2
{margin-left:5px;margin-right:0px;padding-left:10px;padding-right:=
 0px;border-left-width:1px;border-left-style:solid;border-left-color:=
 rgb(204,204,204);margin-top:3px;padding-top:0px;}
aimg
{border:0px;}
body
{font-family:Tahoma;font-size:12pt;}
--></style></head><body><div>thisisareplytoPO200109fromemClient</div=
><divid=3D"signature_old"><divstyle=3D"font-family:Tahoma;font-size:=
 12pt;">--<br/><span><spanclass=3D"__postbox-detected-content__postbox=
-detected-address"style=3D"TEXT-DECORATION:underline;COLOR:rgb(115,133,=
172);PADDING-BOTTOM:0pt;PADDING-TOP:0pt;PADDING-LEFT:0pt;DISPLAY:=
 inline;PADDING-RIGHT:0pt"__postbox-detected-content=3D"__postbox-detect=
ed-address"></span>xxxx<br/>xxxx<br/><b=
r/>xxxx</span></=
div></div><div><br/></div><div><br/></div><div><br/></div>
<div>------OriginalMessage------</div>
<div>From:"xxxx"&lt;<ahref=3D"mailto:xxxx@xxxx.com">xxxx=
@xxxx.com</a>&gt;</div>
<div>To:"xxxx"&lt;<ahref=3D"mailto:xxxx@xxxx.com">a=
xxxx@xxxx.com</a>&gt;</div>
<div>Sent:4/13/20187:06:43PM</div>
<div>Subject:xxxx</div><div><br/></div=
>
<divid=3D"x00b4101ba6e64ce"><blockquotecite=3D"829228972724527.1523671602=
.256660938262939-openerp-129-xxxx.xxxx@ip-1-1-1-1"type=3D"cite"=
 class=3D"cite2">
<tableborder=3D"0"width=3D"100%"cellpadding=3D"0"bgcolor=3D"#ededed"=
 style=3D"padding:20px;background-color:#ededed"summary=3D"o_mail_notif=
ication">
                    <tbody>

                      <!--HEADER-->
                      <tr>
                        <tdalign=3D"center"style=3D"min-width:590px;">
                          <tablewidth=3D"590"border=3D"0"cellpadding=3D=
"0"bgcolor=3D"#009EFB"style=3D"min-width:590px;background-color:rgb(13=
5,90,123);padding:20px;">
                            <tbody><tr>
                              <tdvalign=3D"middle">
                                  <spanstyle=3D"font-size:20px;color:whit=
e;font-weight:bold;">
                                      mangezdessaucisses
                                  </span>
                              </td>
                              <tdvalign=3D"middle"align=3D"right">
                                  <imgsrc=3D"http://erp.xxxx.xxxx/logo.png=
"style=3D"padding:0px;margin:0px;height:auto;width:80px;"alt=3D=
"xxxx"/>
                              </td>
                            </tr>
                          </tbody></table>
                        </td>
                      </tr>

                      <!--CONTENT-->
                      <tr>
                        <tdalign=3D"center"style=3D"min-width:590px;">
                          <tablewidth=3D"590"border=3D"0"cellpadding=3D=
"0"bgcolor=3D"#ffffff"style=3D"min-width:590px;background-color:rgb(25=
5,255,255);padding:20px;">
                            <tbody>
                              <tr><tdvalign=3D"top"style=3D"font-family:A=
rial,Helvetica,sans-serif;color:#555;font-size:14px;">
                                <pstyle=3D"margin:0px0px9px0px;font-s=
ize:13px;font-family:&quot;LucidaGrande&quot;,Helvetica,Verdana,Aria=
l,sans-serif">xxxx.=20
,</p>
<pstyle=3D"margin:0px0px9px0px;font-size:13px;font-family:&quot;Lu=
cidaGrande&quot;,Helvetica,Verdana,Arial,sans-serif">
xxxx.
</p>

<pstyle=3D"margin:0px0px9px0px;font-size:13px;font-family:&quot;Lu=
cidaGrande&quot;,Helvetica,Verdana,Arial,sans-serif">Youcanreply=
tothisemailifyouhaveanyquestions.</p>
<pstyle=3D"margin:0px0px9px0px;font-size:13px;font-family:&quot;Lu=
cidaGrande&quot;,Helvetica,Verdana,Arial,sans-serif">Thankyou,</p>
                              </td>
                            </tr></tbody>
                          </table>
                        </td>
                      </tr>

                      <!--FOOTER-->
                      <tr>
                        <tdalign=3D"center"style=3D"min-width:590px;">
                          <tablewidth=3D"590"border=3D"0"cellpadding=3D=
"0"bgcolor=3D"#009EFB"style=3D"min-width:590px;background-color:rgb(13=
5,90,123);padding:20px;">
                            <tbody><tr>
                              <tdvalign=3D"middle"align=3D"left"style=
=3D"color:#fff;padding-top:10px;padding-bottom:10px;font-size:12px;"=
>
                                xxxx<br/>
                                +1-801-980-4240
                              </td>
                              <tdvalign=3D"middle"align=3D"right"style=
=3D"color:#fff;padding-top:10px;padding-bottom:10px;font-size:12px;"=
>
                                <ahref=3D"http://erp.xxxx.xxxx/info@xxxx-a=
aa.com"style=3D"text-decoration:none;color:white;">info@aust-mfg.com</a>=
<br/>
                                    <ahref=3D"http://www.xxxx=
.com"style=3D"text-decoration:none;color:white;">
                                        http://www.xxxx.com
                                    </a>
                              </td>
                            </tr>
                          </tbody></table>
                        </td>
                      </tr>
                      <tr>
                        <tdalign=3D"center">
                            Poweredby<ahref=3D"https://www.flectrahq.com">Odo=
o</a>.
                        </td>
                      </tr>
                    </tbody>
                </table>
               =20
                <prestyle=3D"white-space:pre-wrap">xxxx.
</pre>
</blockquote></div>
</body></html>
--------=_MB48E455BD-2850-42EC-B1CA-886CDF48905E--"""


MAIL_BOUNCE="""Return-Path:<>
X-Original-To:{to}
Delivered-To:{to}
Received:bymail2.test.ironsky(Postfix)
    id93A83A5F0D;Mon,15Apr201915:41:06+0200(CEST)
Date:Mon,15Apr201915:41:06+0200(CEST)
From:MAILER-DAEMON@mail2.test.ironsky(MailDeliverySystem)
Subject:{subject}
To:{to}
Auto-Submitted:auto-replied
MIME-Version:1.0
Content-Type:multipart/report;report-type=delivery-status;
    boundary="92726A5F09.1555335666/mail2.test.ironsky"
Message-Id:<20190415134106.93A83A5F0D@mail2.test.ironsky>

ThisisaMIME-encapsulatedmessage.

--92726A5F09.1555335666/mail2.test.ironsky
Content-Description:Notification
Content-Type:text/plain;charset=us-ascii

Thisisthemailsystemathostmail2.test.ironsky.

I'msorrytohavetoinformyouthatyourmessagecouldnot
bedeliveredtooneormorerecipients.It'sattachedbelow.

Forfurtherassistance,pleasesendmailtopostmaster.

Ifyoudoso,pleaseincludethisproblemreport.Youcan
deleteyourowntextfromtheattachedreturnedmessage.

                   Themailsystem

<{email_from}>:hosttribulant.com[23.22.38.89]said:550Nosuch
    personatthisaddress.(inreplytoRCPTTOcommand)

--92726A5F09.1555335666/mail2.test.ironsky
Content-Description:Deliveryreport
Content-Type:message/delivery-status

Reporting-MTA:dns;mail2.test.ironsky
X-Postfix-Queue-ID:92726A5F09
X-Postfix-Sender:rfc822;{to}
Arrival-Date:Mon,15Apr201915:40:24+0200(CEST)

Final-Recipient:rfc822;{email_from}
Original-Recipient:rfc822;{email_from}
Action:failed
Status:5.0.0
Remote-MTA:dns;tribulant.com
Diagnostic-Code:smtp;550Nosuchpersonatthisaddress.

--92726A5F09.1555335666/mail2.test.ironsky
Content-Description:UndeliveredMessage
Content-Type:message/rfc822

Return-Path:<{to}>
Received:from[127.0.0.1](host-212-68-194-133.dynamic.voo.be[212.68.194.133])
    (Authenticatedsender:aaa)
    bymail2.test.ironsky(Postfix)withESMTPSAid92726A5F09
    for<{email_from}>;Mon,15Apr201915:40:24+0200(CEST)
DKIM-Signature:v=1;a=rsa-sha256;c=simple/simple;d=test.ironsky;s=mail;
    t=1555335624;bh=x6cSjphxNDiRDMmm24lMAUKtdCFfftM8w/fdUyfoeFs=;
    h=references:Subject:From:Reply-To:To:Date:From;
    b=Bo0BsXAHgKiBfBtMvvO/+KaS9PuuS0+AozL4SxU05jHZcJFc7qFIPEpqkJIdbzNcQ
     wq0PJYclgX7QZDOMm3VHQwcwOxBDXAbdnpfkPM9/wa+FWKfr6ikowMTHHT3CA1qNbe
     h+BQVyBKIvr/LDFPSN2hQmfXWwWupm1lgUhJ07T4=
Content-Type:multipart/mixed;boundary="===============7355787381227985247=="
MIME-Version:1.0
Message-Id:{extra}
references:<670034078674109.1555335454.587288856506348-openerp-32-project.task@aaa>
Subject:Re:Test
From:MitchellAdmin<admin@yourcompany.example.com>
Reply-To:YourCompanyResearch&Development<aaa+catchall@test.ironsky>
To:Raoul<{email_from}>
Date:Mon,15Apr201913:40:24-0000
X-Flectra-Objects:project.project-3,,project.task-32
X-Spam-Status:No,score=-2.0required=5.0tests=ALL_TRUSTED,BAYES_00,
    DKIM_ADSP_NXDOMAIN,HEADER_FROM_DIFFERENT_DOMAINS,HTML_MESSAGE
    shortcircuit=noautolearn=noautolearn_force=noversion=3.4.2
X-Spam-Checker-Version:SpamAssassin3.4.2(2018-09-13)onmail2.test.ironsky

--===============7355787381227985247==
Content-Type:multipart/alternative;boundary="===============8588563873240298690=="
MIME-Version:1.0

--===============8588563873240298690==
Content-Type:text/plain;charset="utf-8"
MIME-Version:1.0
Content-Transfer-Encoding:base64

CgpaYm91bGl1b2l1b2l6ZWYKCi0tCkFkbWluaXN0cmF0b3IKU2VudApieQpbMV0gWW91ckNvbXBh
bnkKCnVzaW5nCk9kb28gWzJdIC4KCgoKWzFdIGh0dHA6Ly93d3cuZXhhbXBsZS5jb20KWzJdIGh0
dHBzOi8vd3d3Lm9kb28uY29tP3V0bV9zb3VyY2U9ZGImdXRtX21lZGl1bT1lbWFpbAo=

--===============8588563873240298690==
Content-Type:text/html;charset="utf-8"
MIME-Version:1.0
Content-Transfer-Encoding:base64

CjxkaXY+CgoKPGRpdj48cD5aYm91bGl1b2l1b2l6ZWY8L3A+PC9kaXY+Cgo8ZGl2IGNsYXNzPSJm
b250LXNpemU6IDEzcHg7Ij48c3BhbiBkYXRhLW8tbWFpbC1xdW90ZT0iMSI+LS0gPGJyIGRhdGEt
by1tYWlsLXF1b3RlPSIxIj4KQWRtaW5pc3RyYXRvcjwvc3Bhbj48L2Rpdj4KPHAgc3R5bGU9ImNv
bG9yOiAjNTU1NTU1OyBtYXJnaW4tdG9wOjMycHg7Ij4KICAgIFNlbnQKICAgIDxzcGFuPgogICAg
YnkKICAgIDxhIHN0eWxlPSJ0ZXh0LWRlY29yYXRpb246bm9uZTsgY29sb3I6ICM4NzVBN0I7IiBo
cmVmPSJodHRwOi8vd3d3LmV4YW1wbGUuY29tIj4KICAgICAgICA8c3Bhbj5Zb3VyQ29tcGFueTwv
c3Bhbj4KICAgIDwvYT4KICAgIAogICAgPC9zcGFuPgogICAgdXNpbmcKICAgIDxhIHRhcmdldD0i
X2JsYW5rIiBocmVmPSJodHRwczovL3d3dy5vZG9vLmNvbT91dG1fc291cmNlPWRiJmFtcDt1dG1f
bWVkaXVtPWVtYWlsIiBzdHlsZT0idGV4dC1kZWNvcmF0aW9uOm5vbmU7IGNvbG9yOiAjODc1QTdC
OyI+T2RvbzwvYT4uCjwvcD4KPC9kaXY+CiAgICAgICAg

--===============8588563873240298690==--

--===============7355787381227985247==--

--92726A5F09.1555335666/mail2.test.ironsky--
"""


MAIL_BOUNCE_QP_RFC822_HEADERS="""\
Received:bymailserver.flectrahq.com(Postfix)
        idEA0B917B8E4;Tue,29Feb202311:11:11+0100(CET)
From:{email_from}
Subject:UndeliveredMailReturnedtoSender
To:{email_to}
Auto-Submitted:auto-replied
MIME-Version:1.0
Content-Type:multipart/report;report-type=delivery-status;
        boundary="DFFDC17AA03.1673346179/mailserver.flectrahq.com"
Message-Id:<40230110102259.EA0B917B8E4@mailserver.flectrahq.com>
Content-Transfer-Encoding:7bit
Delivered-To:{delivered_to}
Return-Path:<>

--DFFDC17AA03.1673346179/mailserver.flectrahq.com
Content-Description:Notification
Content-Type:text/plain;charset=utf-8
Content-Transfer-Encoding:quoted-printable

I'msorrytohavetoinformyouthatyourmessagecouldnot
bedeliveredtooneormorerecipients.

<rdesfrdgtfdrfesd@outlook.com>:host
    outlook-com.olc.protection.outlook.com[104.47.56.33]said:5505.5.0
    Requestedactionnottaken:mailboxunavailable(S2017062302).(inre=
plyto
    RCPTTOcommand)

--DFFDC17AA03.1673346179/mailserver.flectrahq.com
Content-Description:Deliveryreport
Content-Type:message/delivery-status

Reporting-MTA:dns;mailserver.flectrahq.com
X-Postfix-Queue-ID:DFFDC17AA03
X-Postfix-Sender:rfc822;bounce@xxx.flectrahq.com
Arrival-Date:Tue,29Feb202310:10:10+0100(CET)

Final-Recipient:rfc822;rdesfrdgtfdrfesd@outlook.com
Original-Recipient:rfc822;rdesfrdgtfdrfesd@outlook.com
Action:failed
Status:5.5.0
Remote-MTA:dns;outlook-com.olc.protection.outlook.com
Diagnostic-Code:smtp;5505.5.0Requestedactionnottaken:mailbox
    unavailable(S2017062302).

--DFFDC17AA03.1673346179/mailserver.flectrahq.com
Content-Description:UndeliveredMessageHeaders
Content-Type:text/rfc822-headers
Content-Transfer-Encoding:quoted-printable

Return-Path:<bounce@xxx.flectrahq.com>
Received:fromeupp00.flectrahq.com(00.72.79.34.bc.googleusercontent.com[34.=
79.72.00])
        bymailserver.flectrahq.com(Postfix)withESMTPSidDFFDC17AA03;
        Tue,10Jan202311:22:57+0100(CET)
DKIM-Signature:v=3D1;a=3Drsa-sha256;c=3Dsimple/simple;d=3Dxxx.be;
        s=3Dflectra;t=3D1673346178;
        bh=3DYPJOqkUi8B28X1MrRUsgmsL8KRz/ZIkpbYyc6wNITXA=3D;
        h=3Dreferences:Subject:From:Reply-To:To:Date:From;
        b=3DCMqh7mUvpgUw+JpCeGluv1+MZ3y6EsXd0acmsfzpYBjcoy1InvD6FLT1/lQCcgetf
         cGyL/8R4vvDKATyE0AtOIpoYDsbpnMoiYWqaSXnDVuLTrEZzyrK/2j10ZTnHZ2uDTC
         b7wPjFfQ9pted/t6CAUhVT1XydDNalSwEZovy/QI=3D
Message-Id:<368396033905967.1673346177.695352554321289-openerp-11-sale.o=
rder@eupp00>
references:<792105153140463.1673746527.352018594741821-openerp-11-sale.o=
rder@xxx.flectrahq.com><368396033905967.1673346177.695352554321289-openerp-11=
-sale.order@eupp00>
Subject:ThiisaSO(RefSO/11)
From:info@xxx.flectrahq.com
Reply-To:"SO/11"<catchall@xxx.flectrahq.com=
>
To:"rdesfrdgtfdrfesd@outlook.com"<rdesfrdgtfdrfesd@outlook.com>
Date:Tue,29Feb202306:09:06-0000
X-Flectra-Objects:sale.order-11
MIME-Version:1.0
Content-Type:multipart/mixed;boundary=3D"=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=
=3D=3D=3D=3D=3D5706316606908750110=3D=3D"

--DFFDC17AA03.1673346179/mailserver.flectrahq.com--

"""

MAIL_NO_BODY='''\
Return-Path:<{email_from}>
Delivered-To:catchall@xxxx.xxxx
Received:fromin66.mail.ovh.net(unknown[10.101.4.66])
    byvr38.mail.ovh.net(Postfix)withESMTPid4GLCGr70Kyz1myr75
    for<catchall@xxxx.xxxx>;Thu, 8Jul202110:30:12+0000(UTC)
X-Comment:SPFcheckN/Aforlocalconnections-client-ip=213.186.33.59;helo=mail663.ha.ovh.net;envelope-from={email_from};receiver=catchall@xxxx.xxxx
Authentication-Results:in66.mail.ovh.net;dkim=none;dkim-atps=neutral
Delivered-To:xxxx.xxxx-{email_to}
X-ME-Helo:opme11oxm23aub.bagnolet.francetelecom.fr
X-ME-Auth:ZnJlZGVyaWMuYmxhY2hvbjA3QG9yYW5nZS5mcg==
X-ME-Date:Thu,08Jul202112:30:11+0200
X-ME-IP:86.221.151.111
Date:Thu,8Jul202112:30:11+0200(CEST)
From:=?UTF-8?Q?Fr=C3=A9d=C3=A9ric_BLACHON?=<{email_from}>
Reply-To:
    =?UTF-8?Q?Fr=C3=A9d=C3=A9ric_BLACHON?=<{email_from}>
To:{email_to}
Message-ID:<1024471522.82574.1625740211606.JavaMail.open-xchange@opme11oxm23aub.bagnolet.francetelecom.fr>
Subject:transportautorisation19T
MIME-Version:1.0
Content-Type:multipart/mixed;
    boundary="----=_Part_82573_178179506.1625740211587"

------=_Part_82573_178179506.1625740211587
MIME-Version:1.0
Content-Type:text/html;charset=UTF-8
Content-Transfer-Encoding:7bit

<!DOCTYPEhtmlPUBLIC"-//W3C//DTDXHTML1.0Strict//EN""http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<htmlxmlns="http://www.w3.org/1999/xhtml"><head>
    <metahttp-equiv="Content-Type"content="text/html;charset=UTF-8"/>
 </head><bodystyle="font-family:arial,helvetica,sans-serif;font-size:13pt"></body></html>
'''

MAIL_NO_FINAL_RECIPIENT="""\
Return-Path:<bounce-md_9656353.6125275c.v1-f28f7746389e45f0bfbf9faefe9e0dc8@mandrillapp.com>
Delivered-To:catchall@xxxx.xxxx
Received:fromin58.mail.ovh.net(unknown[10.101.4.58])
	byvr46.mail.ovh.net(Postfix)withESMTPid4GvFsq2QLYz1t0N7r
	for<catchall@xxxx.xxxx>;Tue,24Aug202117:07:43+0000(UTC)
Received-SPF:Softfail(mailfrom)identity=mailfrom;client-ip=46.105.72.169;helo=40.mo36.mail-out.ovh.net;envelope-from=bounce-md_9656353.6125275c.v1-f28f7746389e45f0bfbf9faefe9e0dc8@mandrillapp.com;receiver=catchall@xxxx.xxxx
Authentication-Results:in58.mail.ovh.net;
	dkim=pass(1024-bitkey;unprotected)header.d=mandrillapp.comheader.i=bounces-noreply@mandrillapp.comheader.b="TDzUcdJs";
	dkim=pass(1024-bitkey)header.d=mandrillapp.comheader.i=@mandrillapp.comheader.b="MyjddTY5";
	dkim-atps=neutral
Delivered-To:xxxx.xxxx-{email_to}
Authentication-Results:in62.mail.ovh.net;
	dkim=pass(1024-bitkey;unprotected)header.d=mandrillapp.comheader.i=bounces-noreply@mandrillapp.comheader.b="TDzUcdJs";
	dkim=pass(1024-bitkey)header.d=mandrillapp.comheader.i=@mandrillapp.comheader.b="MyjddTY5";
	dkim-atps=neutral
From:MAILER-DAEMON<bounces-noreply@mandrillapp.com>
Subject:UndeliveredMailReturnedtoSender
To:{email_to}
X-Report-Abuse:Pleaseforwardacopyofthismessage,includingallheaders,toabuse@mandrill.com
X-Report-Abuse:Youcanalsoreportabusehere:http://mandrillapp.com/contact/abuse?id=9656353.f28f7746389e45f0bfbf9faefe9e0dc8
X-Mandrill-User:md_9656353
Feedback-ID:9656353:9656353.20210824:md
Message-Id:<9656353.20210824170740.6125275cf21879.17950539@mail9.us4.mandrillapp.com>
Date:Tue,24Aug202117:07:40+0000
MIME-Version:1.0
Content-Type:multipart/report;boundary="_av-UfLe6y6qxNo54-urtAxbJQ"

--_av-UfLe6y6qxNo54-urtAxbJQ
Content-Type:text/plain;charset=utf-8
Content-Transfer-Encoding:7bit

    ---Thefollowingaddresseshaddeliveryproblems---

<{email_from}>  (5.7.1<{email_from}>:Recipientaddressrejected:Accessdenied)


--_av-UfLe6y6qxNo54-urtAxbJQ
Content-Type:message/delivery-status
Content-Transfer-Encoding:7bit

Original-Recipient:<{email_from}>
Action:failed
Diagnostic-Code:smtp;5545.7.1<{email_from}>:Recipientaddressrejected:Accessdenied
Remote-MTA:10.245.192.40



--_av-UfLe6y6qxNo54-urtAxbJQ--"""
