# -*- coding: utf-8 -*-
"""Sinh trang web tĩnh cho sản phẩm HiTA từ san_pham.json.
Chạy:  python tao_trang.py [địa chỉ gốc, mặc định lấy từ tep CNAME hoặc github.io]
Ra:    index.html, 01/<GTIN13>/index.html (trang đích của QR), 01/0<GTIN13>/index.html (GS1 Digital Link GTIN-14, chuyển về trang trên), style.css, 404.html
"""
import html
import json
import os
import re
import sys

GOC = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(GOC, "san_pham.json"), encoding="utf-8"))
BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://daithanhdoan65.github.io/hita-ca-phe").rstrip("/")
e = html.escape

CSS = """
:root{--nen:#f7f0e4;--the:#fffaf1;--chu:#2b1d14;--phu:#6b5a4b;--nhan:#8a2a3a;--vang:#b87a14;--vien:#e6d6b8;--nut:#8a2a3a;--nut-chu:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--nen:#171210;--the:#221a16;--chu:#f1e8da;--phu:#b9a995;--nhan:#e0788a;--vang:#e2a948;--vien:#3a2e27;--nut:#c44a5e;--nut-chu:#fff}}
*{box-sizing:border-box}
body{margin:0;background:var(--nen);color:var(--chu);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--nhan)}
.dau{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--the);border-bottom:1px solid var(--vien)}
.dau img{width:44px;height:44px;border-radius:50%;object-fit:cover}
.dau b{display:block;font-size:17px;letter-spacing:.2px}
.dau span{font-size:13px;color:var(--phu)}
main{max-width:640px;margin:0 auto;padding:0 16px 40px}
.anh{margin:16px 0 0;border-radius:16px;overflow:hidden;background:var(--the);border:1px solid var(--vien)}
.anh img{display:block;width:100%;height:auto}
h1{font-size:24px;line-height:1.25;margin:18px 0 6px}
h2{font-size:18px;margin:0 0 10px;color:var(--nhan)}
.chip{display:inline-block;padding:3px 12px;border-radius:999px;background:var(--the);border:1px solid var(--vien);font-size:14px;margin:0 6px 6px 0}
.chip.dam{background:var(--nhan);border-color:var(--nhan);color:#fff}
.xacthuc{margin:14px 0;padding:12px 14px;border-radius:12px;background:var(--the);border:1px solid var(--vien);border-left:5px solid var(--vang);font-size:15px}
.xacthuc b{color:var(--vang)}
section{margin:22px 0;padding:16px;background:var(--the);border:1px solid var(--vien);border-radius:14px}
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
footer{max-width:640px;margin:0 auto;padding:0 16px 32px;color:var(--phu);font-size:13px}
@media (min-width:560px){.luoi{grid-template-columns:repeat(3,1fr)}}
"""


def gtin_ok(g):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(g[:12]))
    return (10 - s % 10) % 10 == int(g[12])


def kl(sp):
    return "%d g" % sp["kl"]


def ten_day_du(sp):
    return "%s %s" % (D["dong"][sp["dong"]]["ten"], kl(sp))


def url_sp(sp, tuyet_doi=False):
    p = "01/%s/" % sp["gtin"]
    return (BASE + "/" + p) if tuyet_doi else p


def video_html(url):
    if not url:
        return ""
    m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})", url)
    if m:
        kh = '<iframe src="https://www.youtube-nocookie.com/embed/%s" title="Video sản phẩm" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe>' % m.group(1)
    elif url.lower().endswith((".mp4", ".webm")):
        kh = '<video controls preload="metadata" playsinline src="%s"></video>' % e(url)
    else:
        return '<section><h2>Video</h2><div class="nut"><a href="%s" rel="noopener">Xem video sản phẩm</a></div></section>' % e(url)
    return '<section><h2>Video sản phẩm</h2><div class="video">%s</div></section>' % kh


DAU = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(tieu_de)s</title>
<meta name="description" content="%(mo_ta)s">
<meta property="og:title" content="%(tieu_de)s"><meta property="og:description" content="%(mo_ta)s">
<meta property="og:type" content="website"><meta property="og:image" content="%(anh_og)s">
<link rel="icon" href="%(goc)sanh/logo.jpeg">
<link rel="stylesheet" href="%(goc)sstyle.css">
%(json_ld)s</head><body>
<div class="dau"><img src="%(goc)sanh/logo.jpeg" alt="HiTA Roasters"><div><b>HiTA Cà Phê</b><span>HiTA Roasters</span></div></div>
"""

CUOI = """<footer><p>%(cong_ty)s<br>%(dia_chi)s</p><p>Thông tin sản phẩm do HiTA Roasters cung cấp. Ngày sản xuất xem trên bao bì.</p></footer>
</body></html>
"""


def lien_he():
    return ('<section><h2>Về HiTA Roasters</h2><p>%s</p>'
            '<div class="nut"><a href="%s" rel="noopener">Website HiTA</a>'
            '<a class="phu" href="%s" rel="noopener">Chat Zalo</a>'
            '<a class="phu" href="tel:%s">Gọi %s</a></div></section>'
            % (e(D["gioi_thieu"]), e(D["website"]), e(D["zalo"]), D["dien_thoai_quoc_te"], e(D["dien_thoai"])))


def trang_sp(sp):
    dong = D["dong"][sp["dong"]]
    ten = ten_day_du(sp)
    goc = "../../"
    ld = {
        "@context": "https://schema.org", "@type": "Product", "name": ten, "gtin13": sp["gtin"],
        "image": BASE + "/anh/" + dong["anh"], "description": dong["gioi_thieu"],
        "brand": {"@type": "Brand", "name": D["thuong_hieu"]},
        "manufacturer": {"@type": "Organization", "name": D["cong_ty"], "url": D["website"]},
        "url": url_sp(sp, True),
    }
    o = DAU % dict(
        tieu_de=e(ten + " | HiTA Cà Phê"), mo_ta=e(dong["gioi_thieu"]), anh_og=e(BASE + "/anh/" + dong["anh"]), goc=goc,
        json_ld='<script type="application/ld+json">%s</script>\n' % json.dumps(ld, ensure_ascii=False))
    o += '<main><figure class="anh"><img src="%sanh/%s" alt="%s"></figure>' % (goc, e(dong["anh"]), e(ten))
    o += '<h1>%s</h1><span class="chip dam">%s</span><span class="chip">%s</span><span class="chip">Mã vạch %s</span>' % (
        e(D["dong"][sp["dong"]]["ten"]), kl(sp), e(dong["dang"]), sp["gtin"])
    o += '<div class="xacthuc"><b>Sản phẩm chính hãng HiTA Roasters.</b> Mã GTIN %s đã đăng ký tại Trung tâm Mã số mã vạch quốc gia (GS1 Việt Nam).</div>' % sp["gtin"]
    o += '<section><h2>Thông tin sản phẩm</h2><dl>'
    o += '<dt>Thành phần</dt><dd>%s</dd>' % e(dong["thanh_phan"])
    o += '<dt>Khối lượng tịnh</dt><dd>%s</dd>' % kl(sp)
    if dong["do_am"]:
        o += '<dt>Độ ẩm</dt><dd>%s</dd>' % e(dong["do_am"])
    o += '<dt>Hạn sử dụng</dt><dd>%s</dd>' % e(D["han_dung"])
    o += '<dt>Hướng dẫn bảo quản</dt><dd>%s</dd>' % e(D["bao_quan"])
    o += '<dt>Cảnh báo</dt><dd>%s</dd>' % e(D["canh_bao"])
    o += '<dt>Nhà sản xuất</dt><dd>%s<br>%s</dd></dl></section>' % (e(D["cong_ty"]), e(D["dia_chi"]))
    if dong["cach_pha"]:
        o += '<section><h2>Cách pha chế (phin)</h2><ol>%s</ol></section>' % "".join("<li>%s</li>" % e(b) for b in dong["cach_pha"])
    o += video_html(sp.get("video") or D.get("video_gioi_thieu"))
    khac = [s for s in D["san_pham"] if s["gtin"] != sp["gtin"]]
    o += '<section><h2>Sản phẩm khác của HiTA</h2><div class="luoi">%s</div></section>' % "".join(
        '<a class="the" href="%s../%s/"><img src="%sanh/%s" alt="" loading="lazy"><span>%s<br><small>%s</small></span></a>' % (
            "", s["gtin"], goc, e(D["dong"][s["dong"]]["anh"]), e(D["dong"][s["dong"]]["ten_ngan"]), kl(s)) for s in khac)
    o += lien_he() + "</main>" + CUOI % D
    return o


def trang_chu():
    goc = ""
    o = DAU % dict(tieu_de="HiTA Cà Phê - Thông tin sản phẩm", mo_ta=e(D["gioi_thieu"]), anh_og=e(BASE + "/anh/" + D["dong"]["bot"]["anh"]),
                   goc=goc, json_ld="")
    o += '<main><h1>HiTA Cà Phê</h1><p>%s</p>' % e(D["gioi_thieu"])
    o += video_html(D.get("video_gioi_thieu"))
    o += '<section><h2>Sản phẩm</h2><div class="luoi">%s</div></section>' % "".join(
        '<a class="the" href="01/%s/"><img src="anh/%s" alt="" loading="lazy"><span>%s<br><small>%s</small></span></a>' % (
            s["gtin"], e(D["dong"][s["dong"]]["anh"]), e(D["dong"][s["dong"]]["ten_ngan"]), kl(s)) for s in D["san_pham"])
    o += lien_he() + "</main>" + CUOI % D
    return o


def chuyen_huong(den):
    return ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="refresh" content="0;url=%s"><link rel="canonical" href="%s"><title>HiTA Cà Phê</title></head>'
            '<body><a href="%s">HiTA Cà Phê</a></body></html>' % (den, den, den))


def ghi(duong, noi_dung):
    f = os.path.join(GOC, duong)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w", encoding="utf-8", newline="\n").write(noi_dung)


def main():
    for sp in D["san_pham"]:
        assert len(sp["gtin"]) == 13 and gtin_ok(sp["gtin"]), "GTIN sai số kiểm tra: " + sp["gtin"]
        ghi("01/%s/index.html" % sp["gtin"], trang_sp(sp))
        ghi("01/0%s/index.html" % sp["gtin"], chuyen_huong(url_sp(sp, True)))
    ghi("index.html", trang_chu())
    ghi("404.html", chuyen_huong(BASE + "/"))
    ghi("style.css", CSS.strip() + "\n")
    ghi(".nojekyll", "")
    print("Da sinh %d trang san pham, goc %s" % (len(D["san_pham"]), BASE))


if __name__ == "__main__":
    main()
