# -*- coding: utf-8 -*-
"""Sinh trang web tĩnh "Gian Hàng": một trang chủ nền tảng + mỗi cơ sở một gian hàng.

Dữ liệu: nen_tang.json (tên nền tảng, địa chỉ gốc) và co_so/<slug>/co_so.json (mỗi cơ sở một thư mục, ảnh để ở co_so/<slug>/anh/).
Chạy:  python tao_trang.py [địa chỉ gốc]      (không truyền thì lấy "dia_chi_goc" trong nen_tang.json)
Ra:
  index.html                      trang chủ: danh sách gian hàng
  <slug>/index.html               gian hàng của cơ sở
  01/<GTIN13>/index.html          trang sản phẩm = đích của mã QR (cấu trúc GS1 Digital Link; GTIN toàn cầu nên không cần <slug>)
  01/0<GTIN13>/index.html         dạng GTIN-14, chuyển về trang trên
Thêm cơ sở mới: chép co_so/_mau sang co_so/<slug>, điền, chạy lại. Xem README.md.
"""
import glob
import html
import json
import os
import re
import sys

GOC = os.path.dirname(os.path.abspath(__file__))
e = html.escape
RESERVED = {"01", "co_so", "style.css", "index.html", "404.html"}


def doc(p):
    return json.load(open(p, encoding="utf-8"))


NT = doc(os.path.join(GOC, "nen_tang.json"))
BASE = (sys.argv[1] if len(sys.argv) > 1 else NT["dia_chi_goc"]).rstrip("/")
COSO = {}
for f in sorted(glob.glob(os.path.join(GOC, "co_so", "*", "co_so.json"))):
    c = doc(f)
    if os.path.basename(os.path.dirname(f)).startswith("_"):
        continue
    assert re.fullmatch(r"[a-z0-9-]+", c["slug"]) and c["slug"] not in RESERVED, "slug sai: " + c["slug"]
    assert c["slug"] == os.path.basename(os.path.dirname(f)), "slug khong khop ten thu muc: " + c["slug"]
    COSO[c["slug"]] = c

CSS = """
:root{--nen:#f6f1e7;--the:#fffdf8;--chu:#241b14;--phu:#6a5d50;--nhan:#8a2a3a;--vang:#b87a14;--vien:#e4d8c2;--nut:#8a2a3a;--nut-chu:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--nen:#151210;--the:#201a16;--chu:#f1e9dc;--phu:#b7a994;--vang:#e2a948;--vien:#3a2f27}}
*{box-sizing:border-box}
body{margin:0;background:var(--nen);color:var(--chu);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--nhan)}
.dau{display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--the);border-bottom:1px solid var(--vien)}
.dau img{width:40px;height:40px;border-radius:50%;object-fit:cover;flex:none}
.dau a{text-decoration:none;color:inherit;display:flex;align-items:center;gap:12px;min-width:0}
.dau b{display:block;font-size:16px;line-height:1.2}
.dau span{font-size:12px;color:var(--phu)}
.dau .nt{margin-left:auto;font-size:13px;color:var(--phu);white-space:nowrap}
main{max-width:680px;margin:0 auto;padding:0 16px 40px}
.bia{position:relative;margin:0;height:210px;overflow:hidden;background:var(--the)}
.bia img{width:100%;height:100%;object-fit:cover;object-position:center 35%;display:block}
.bia:after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.55),transparent 60%)}
.bia h1{position:absolute;left:16px;right:16px;padding:0;bottom:12px;margin:0;color:#fff;z-index:1;font-size:26px;line-height:1.2;text-shadow:0 1px 6px rgba(0,0,0,.5)}
.bia h1 small{display:block;font-size:14px;font-weight:400;opacity:.92;margin-top:2px}
.anh{margin:16px 0 0;border-radius:16px;overflow:hidden;background:var(--the);border:1px solid var(--vien)}
.anh img{display:block;width:100%;height:auto}
h1{font-size:24px;line-height:1.25;margin:18px 0 6px}
h2{font-size:18px;margin:0 0 10px;color:var(--nhan)}
.chip{display:inline-block;padding:3px 12px;border-radius:999px;background:var(--the);border:1px solid var(--vien);font-size:14px;margin:0 6px 6px 0;color:inherit;text-decoration:none}
.chip.dam{background:var(--nut);border-color:var(--nut);color:var(--nut-chu)}
.vet{font-size:13px;color:var(--phu);margin:14px 0 0}
.vet a{color:var(--phu)}
.xacthuc{margin:14px 0;padding:12px 14px;border-radius:12px;background:var(--the);border:1px solid var(--vien);border-left:5px solid var(--vang);font-size:15px}
.xacthuc b{color:var(--vang)}
section{margin:20px 0;padding:16px;background:var(--the);border:1px solid var(--vien);border-radius:14px}
dl{margin:0}
dt{font-size:13px;color:var(--phu);margin-top:10px}
dt:first-child{margin-top:0}
dd{margin:2px 0 0}
ol{margin:0;padding-left:22px}
ol li{margin:6px 0}
.video{position:relative;padding-top:56.25%;border-radius:12px;overflow:hidden;background:#000}
.video iframe,.video video{position:absolute;inset:0;width:100%;height:100%;border:0}
.nut{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.nut a{flex:1 1 140px;text-align:center;padding:12px 14px;border-radius:12px;background:var(--nut);color:var(--nut-chu);text-decoration:none;font-weight:600}
.nut a.phu{background:transparent;color:var(--nhan);border:1.5px solid var(--nhan)}
.luoi{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.the{display:block;text-decoration:none;color:inherit;border:1px solid var(--vien);border-radius:12px;overflow:hidden;background:var(--the)}
.the img{display:block;width:100%;aspect-ratio:3/4;object-fit:cover}
.the span{display:block;padding:8px 10px 10px;font-size:14px;line-height:1.35}
.the small{color:var(--phu)}
.sp{display:flex;gap:12px;padding:12px 0;border-top:1px solid var(--vien)}
.sp:first-of-type{border-top:0;padding-top:0}
.sp img{width:84px;height:112px;object-fit:cover;border-radius:10px;flex:none}
.sp b{display:block;line-height:1.3}
.sp p{margin:4px 0 8px;font-size:14px;color:var(--phu)}
.gh{display:flex;gap:14px;align-items:center;text-decoration:none;color:inherit;padding:14px;border:1px solid var(--vien);border-radius:14px;background:var(--the);margin-bottom:12px}
.gh img.lg{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none}
.gh b{display:block;font-size:17px}
.gh span{display:block;font-size:14px;color:var(--phu)}
.gh i{margin-left:auto;font-style:normal;font-size:22px;color:var(--nhan)}
footer{max-width:680px;margin:0 auto;padding:0 16px 32px;color:var(--phu);font-size:13px}
@media (min-width:560px){.luoi{grid-template-columns:repeat(3,1fr)}}
"""


def gtin_ok(g):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(g[:12]))
    return (10 - s % 10) % 10 == int(g[12])


def ra(slug, f):
    return "co_so/%s/anh/%s" % (slug, f)


def tuyet_doi(p):
    return BASE + "/" + p


def kl(sp):
    return "%d g" % sp["kl"]


def video_html(url, nhan="Video"):
    if not url:
        return ""
    m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})", url)
    if m:
        kh = '<iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>' % (m.group(1), e(nhan))
    elif url.lower().endswith((".mp4", ".webm")):
        kh = '<video controls preload="metadata" playsinline src="%s"></video>' % e(url)
    else:
        return '<section><h2>%s</h2><div class="nut"><a href="%s" rel="noopener">Xem video</a></div></section>' % (e(nhan), e(url))
    return '<section><h2>%s</h2><div class="video">%s</div></section>' % (e(nhan), kh)


def theme(c):
    if not c:
        return ""
    return ("<style>:root{--nhan:%s;--nut:%s}@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--nhan:%s}}</style>\n"
            % (c["mau"], c["mau"], c["mau_toi"]))


def khung(goc, tieu_de, mo_ta, anh_og, dau, than, c=None, ld="", url=""):
    o = ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
         '<title>%s</title>\n<meta name="description" content="%s">\n'
         '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website">'
         '<meta property="og:image" content="%s"><meta property="og:url" content="%s">\n'
         '<link rel="stylesheet" href="%sstyle.css">\n%s%s</head><body>\n'
         % (e(tieu_de), e(mo_ta), e(tieu_de), e(mo_ta), e(anh_og), e(url), goc, theme(c or NT), ld))
    o += dau + "\n" + than
    nguoi = ("<p>%s<br>%s</p>" % (e(c["cong_ty"]), e(c["dia_chi"]))) if c else ""
    o += ('<footer>%s<p>Thông tin sản phẩm do cơ sở cung cấp. Ngày sản xuất xem trên bao bì.<br>'
          '<a href="%s">%s</a> - mỗi cơ sở một gian hàng thương hiệu.</p></footer>\n</body></html>\n' % (nguoi, goc or "./", e(NT["ten"])))
    return o


def dau_co_so(c, goc):
    return ('<div class="dau"><a href="%s%s/"><img src="%s%s" alt=""><div><b>%s</b><span>%s</span></div></a>'
            '<a class="nt" href="%s">%s</a></div>' % (goc, c["slug"], goc, ra(c["slug"], c["logo"]), e(c["ten"]), e(c["nganh"]), goc or "./", e(NT["ten_ngan"])))


def lien_he(c):
    n = ""
    if c.get("website"):
        n += '<a href="%s" rel="noopener">Website</a>' % e(c["website"])
    if c.get("zalo"):
        n += '<a class="phu" href="%s" rel="noopener">Chat Zalo</a>' % e(c["zalo"])
    if c.get("dien_thoai_quoc_te"):
        n += '<a class="phu" href="tel:%s">Gọi %s</a>' % (c["dien_thoai_quoc_te"], e(c["dien_thoai"]))
    if c.get("email"):
        n += '<a class="phu" href="mailto:%s">Gửi email</a>' % e(c["email"])
    return '<section><h2>Liên hệ</h2><p>%s</p><div class="nut">%s</div></section>' % (e(c["dia_chi"]), n)


def trang_sp(c, sp):
    goc = "../../"
    s = c["slug"]
    d = c["dong"][sp["dong"]]
    ten = "%s %s" % (d["ten"], kl(sp))
    url = tuyet_doi("01/%s/" % sp["gtin"])
    ld = '<script type="application/ld+json">%s</script>\n' % json.dumps({
        "@context": "https://schema.org", "@type": "Product", "name": ten, "gtin13": sp["gtin"],
        "image": tuyet_doi(ra(s, d["anh"])), "description": d["gioi_thieu"],
        "brand": {"@type": "Brand", "name": c["ten"]},
        "manufacturer": {"@type": "Organization", "name": c["cong_ty"], "url": c.get("website", "")}, "url": url}, ensure_ascii=False)
    t = '<main><figure class="anh"><img src="%s%s" alt="%s"></figure>' % (goc, ra(s, d["anh"]), e(ten))
    t += '<h1>%s</h1><span class="chip dam">%s</span><span class="chip">%s</span><span class="chip">Mã vạch %s</span>' % (e(d["ten"]), kl(sp), e(d["dang"]), sp["gtin"])
    t += '<div class="xacthuc"><b>Sản phẩm chính hãng %s.</b> Mã GTIN %s đã đăng ký tại Trung tâm Mã số mã vạch quốc gia (GS1 Việt Nam).</div>' % (e(c["ten"]), sp["gtin"])
    t += '<div class="nut"><a href="%s%s/">Vào gian hàng %s</a></div>' % (goc, s, e(c["ten"]))
    t += '<section><h2>Thông tin sản phẩm</h2><dl><dt>Thành phần</dt><dd>%s</dd><dt>Khối lượng tịnh</dt><dd>%s</dd>' % (e(d["thanh_phan"]), kl(sp))
    if d.get("do_am"):
        t += '<dt>Độ ẩm</dt><dd>%s</dd>' % e(d["do_am"])
    t += '<dt>Hạn sử dụng</dt><dd>%s</dd><dt>Hướng dẫn bảo quản</dt><dd>%s</dd><dt>Cảnh báo</dt><dd>%s</dd>' % (e(c["han_dung"]), e(c["bao_quan"]), e(c["canh_bao"]))
    t += '<dt>Nhà sản xuất</dt><dd>%s<br>%s</dd></dl></section>' % (e(c["cong_ty"]), e(c["dia_chi"]))
    if d.get("cach_pha"):
        t += '<section><h2>Cách pha chế (phin)</h2><ol>%s</ol></section>' % "".join("<li>%s</li>" % e(b) for b in d["cach_pha"])
    t += video_html(sp.get("video") or c.get("video_gioi_thieu"), "Video sản phẩm")
    khac = [x for x in c["san_pham"] if x["gtin"] != sp["gtin"]]
    if khac:
        t += '<section><h2>Sản phẩm khác của %s</h2><div class="luoi">%s</div></section>' % (e(c["ten"]), "".join(
            '<a class="the" href="../%s/"><img src="%s%s" alt="" loading="lazy"><span>%s<br><small>%s</small></span></a>' % (
                x["gtin"], goc, ra(s, c["dong"][x["dong"]]["anh"]), e(c["dong"][x["dong"]]["ten_ngan"]), kl(x)) for x in khac))
    t += lien_he(c) + "</main>"
    return khung(goc, ten + " | " + c["ten"], d["gioi_thieu"], tuyet_doi(ra(s, d["anh"])), dau_co_so(c, goc), t, c, ld, url)


def trang_co_so(c):
    goc = "../"
    s = c["slug"]
    t = '<div class="bia"><img src="%s%s" alt=""><h1>%s<small>%s</small></h1></div><main>' % (goc, ra(s, c["anh_bia"]), e(c["ten"]), e(c.get("khau_hieu", "")))
    t += '<p style="margin-top:16px"><span class="chip dam">%s</span></p><p>%s</p>' % (e(c["nganh"]), e(c["gioi_thieu"]))
    t += video_html(c.get("video_gioi_thieu"), "Video giới thiệu")
    t += '<section><h2>Sản phẩm</h2>'
    for k, d in c["dong"].items():
        sps = [x for x in c["san_pham"] if x["dong"] == k]
        if not sps:
            continue
        t += '<div class="sp"><img src="%s%s" alt="" loading="lazy"><div><b>%s</b><p>%s</p>%s</div></div>' % (
            goc, ra(s, d["anh"]), e(d["ten"]), e(d["dang"]),
            "".join('<a class="chip" href="%s01/%s/">%s</a>' % (goc, x["gtin"], kl(x)) for x in sps))
    t += '</section>' + lien_he(c) + '</main>'
    return khung(goc, c["ten"] + " | " + NT["ten"], c["gioi_thieu"], tuyet_doi(ra(s, c["anh_bia"])), dau_co_so(c, goc), t, c, "", tuyet_doi(s + "/"))


def trang_chu():
    d = '<div class="dau"><a href="./"><div><b>%s</b><span>Quét mã trên bao bì để xem thông tin sản phẩm</span></div></a></div>' % e(NT["ten"])
    t = '<main><h1>%s</h1><p>%s</p><section><h2>Các gian hàng</h2>' % (e(NT["ten"]), e(NT["mo_ta"]))
    for c in COSO.values():
        t += '<a class="gh" href="%s/"><img class="lg" src="%s" alt=""><div><b>%s</b><span>%s - %d sản phẩm</span></div><i>&rsaquo;</i></a>' % (
            c["slug"], ra(c["slug"], c["logo"]), e(c["ten"]), e(c["nganh"]), len(c["san_pham"]))
    t += '</section></main>'
    return khung("", NT["ten"], NT["mo_ta"], "", d, t, None, "", BASE + "/")


def chuyen_huong(den):
    return ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="refresh" content="0;url=%s"><link rel="canonical" href="%s"><title>%s</title></head>'
            '<body><a href="%s">%s</a></body></html>' % (den, den, e(NT["ten"]), den, e(NT["ten"])))


def ghi(duong, nd):
    f = os.path.join(GOC, duong)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w", encoding="utf-8", newline="\n").write(nd)


def main():
    da = {}
    for c in COSO.values():
        ghi("%s/index.html" % c["slug"], trang_co_so(c))
        for sp in c["san_pham"]:
            g = sp["gtin"]
            assert len(g) == 13 and gtin_ok(g), "GTIN sai so kiem tra: " + g
            assert g not in da, "GTIN trung giua %s va %s" % (c["slug"], da.get(g))
            assert sp["dong"] in c["dong"], "dong khong co: %s %s" % (c["slug"], sp["dong"])
            for f in (c["dong"][sp["dong"]]["anh"], c["logo"], c["anh_bia"]):
                assert os.path.exists(os.path.join(GOC, ra(c["slug"], f))), "thieu anh: " + ra(c["slug"], f)
            da[g] = c["slug"]
            ghi("01/%s/index.html" % g, trang_sp(c, sp))
            ghi("01/0%s/index.html" % g, chuyen_huong(tuyet_doi("01/%s/" % g)))
    ghi("index.html", trang_chu())
    ghi("404.html", chuyen_huong(BASE + "/"))
    ghi("style.css", CSS.strip() + "\n")
    ghi(".nojekyll", "")
    ghi("danh_sach_ma.json", json.dumps({g: {"co_so": s, "url": tuyet_doi("01/%s/" % g)} for g, s in da.items()}, ensure_ascii=False, indent=1) + "\n")
    print("Gian hang: %d, san pham: %d, goc %s" % (len(COSO), len(da), BASE))


if __name__ == "__main__":
    main()
