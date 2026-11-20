# -*- coding: utf-8 -*-
"""Sinh trang web tĩnh "Gian Hàng": một trang chủ nền tảng + mỗi cơ sở một gian hàng.

Dữ liệu: nen_tang.json (tên nền tảng, địa chỉ gốc) và co_so/<slug>/co_so.json (mỗi cơ sở một thư mục;
ảnh để ở co_so/<slug>/anh/, video .mp4 để ở co_so/<slug>/video/ hoặc điền link YouTube).
Chạy:  python tao_trang.py [địa chỉ gốc]      (không truyền thì lấy "dia_chi_goc" trong nen_tang.json)
Ra:
  index.html                      trang chủ: danh sách gian hàng
  <slug>/index.html               gian hàng của cơ sở
  01/<GTIN13>/index.html          trang sản phẩm = đích của mã QR (cấu trúc GS1 Digital Link; GTIN toàn cầu nên không cần <slug>)
  01/0<GTIN13>/index.html         dạng GTIN-14, chuyển về trang trên
  danh_sach_ma.json               GTIN -> địa chỉ (cho tao_qr.py)
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
RESERVED = {"01", "co_so", "font", "style.css", "index.html", "404.html"}


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

# Phong cách quán cà phê: nền espresso đậm, chữ kem, điểm nhấn vàng caramel; phần thân màu kem. Chữ tiêu đề Playfair Display (lưu sẵn trong font/).
CSS = """
@font-face{font-family:"Playfair Display";font-weight:700;font-style:normal;font-display:swap;src:url(font/pf700.ttf) format("truetype")}
:root{--ca:#1b110c;--ca2:#2b1b12;--kem:#f6ecdb;--vang:#e6ad4f;--nen:#f6ecdb;--the:#fffaf0;--chu:#2a1c14;--phu:#66554a;--vien:#e2d1b4;--nhan:#8a2a3a;--nut:#8a2a3a;--nut-chu:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--nen:#150e0a;--the:#241a13;--chu:#f4eadb;--phu:#c2b19a;--vien:#3d2e24}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--nen);color:var(--chu);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--nhan)}
h1,h2,h3,.serif{font-family:"Playfair Display",Georgia,"Times New Roman",serif;font-weight:700;letter-spacing:.2px}
.w{max-width:980px;margin:0 auto;padding:0 18px}
.dau{position:sticky;top:0;z-index:5;background:var(--ca);color:var(--kem);border-bottom:2px solid var(--vang)}
.dau .w{display:flex;align-items:center;gap:12px;height:58px}
.dau a{color:inherit;text-decoration:none;display:flex;align-items:center;gap:11px;min-width:0}
.dau img{width:38px;height:38px;border-radius:50%;object-fit:cover;flex:none;border:2px solid var(--vang)}
.dau b{display:block;font-size:17px;line-height:1.15}
.dau span{display:block;font-size:12px;opacity:.75}
.dau .nt{margin-left:auto;font-size:13px;opacity:.85;white-space:nowrap}
.hero{position:relative;background:var(--ca);color:var(--kem);overflow:hidden;min-height:430px;display:flex;align-items:flex-end}
.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 30%;opacity:.62}
.hero:before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(to top,var(--ca) 4%,rgba(27,17,12,.55) 55%,rgba(27,17,12,.25))}
.hero .w{position:relative;z-index:2;width:100%;padding-bottom:64px;padding-top:60px}
.tag{display:inline-block;padding:4px 14px;border:1.5px solid var(--vang);border-radius:999px;color:var(--vang);font-size:13px;letter-spacing:1.4px;text-transform:uppercase;font-weight:600}
.hero h1{font-size:44px;line-height:1.1;margin:14px 0 6px;color:#fff}
.hero .kh{font-size:20px;color:var(--vang);margin:0 0 20px;font-family:"Playfair Display",Georgia,serif}
.btn,.nut a{display:inline-block;text-align:center;padding:13px 22px;border-radius:999px;background:var(--nut);color:var(--nut-chu);text-decoration:none;font-weight:700;font-size:15px;border:2px solid var(--nut)}
.btn.vang{background:var(--vang);border-color:var(--vang);color:var(--ca)}
.btn.vien,.nut a.phu{background:transparent;color:var(--nhan);border-color:var(--nhan)}
.dem .btn.vien,.dem .nut a.phu,.hero .btn.vien{color:var(--kem);border-color:rgba(246,236,219,.7)}
.dem .nut a{background:var(--vang);border-color:var(--vang);color:var(--ca)}
.dem .nut a.phu{background:transparent;color:var(--kem);border-color:rgba(246,236,219,.7)}
.hang{display:flex;flex-wrap:wrap;gap:10px}
.nut{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.nut a{flex:1 1 150px}
.dem{background:var(--ca);color:var(--kem);padding:44px 0}
.dem h2{color:var(--vang)}
.dem a{color:var(--vang)}
.moi{padding:44px 0}
h2{font-size:30px;line-height:1.2;margin:0 0 6px}
.phude{margin:0 0 22px;color:var(--phu)}
.dem .phude{color:rgba(246,236,219,.78)}
.mach{display:grid;grid-template-columns:1fr;gap:12px;margin:-26px auto 0;position:relative;z-index:3}
.mach div{background:var(--the);border:1px solid var(--vien);border-top:3px solid var(--vang);border-radius:14px;padding:16px 18px;box-shadow:0 8px 22px rgba(27,17,12,.14)}
.mach b{display:block;font-family:"Playfair Display",Georgia,serif;font-size:18px;margin-bottom:2px}
.mach span{font-size:14px;color:var(--phu)}
.luoi{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.sp{background:var(--the);border:1px solid var(--vien);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 6px 18px rgba(27,17,12,.08)}
.sp img{display:block;width:100%;aspect-ratio:3/4;object-fit:cover}
.sp .nd{padding:12px 14px 16px;display:flex;flex-direction:column;gap:6px;flex:1}
.sp h3{font-size:17px;line-height:1.3;margin:0}
.sp .d{font-size:13px;color:var(--phu);letter-spacing:.6px;text-transform:uppercase}
.kl{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:6px}
.kl a{padding:6px 16px;border-radius:999px;border:1.5px solid var(--nhan);color:var(--nhan);text-decoration:none;font-weight:700;font-size:14px}
.kl a:hover{background:var(--nhan);color:#fff}
.khung-video{display:flex;flex-direction:column;align-items:center;gap:22px}
.dt{width:100%;max-width:300px;aspect-ratio:9/16;border-radius:26px;border:3px solid var(--vang);overflow:hidden;background:#000;box-shadow:0 14px 40px rgba(0,0,0,.5)}
.dt video,.dt iframe{width:100%;height:100%;display:block;border:0;object-fit:cover}
.video{position:relative;padding-top:56.25%;border-radius:14px;overflow:hidden;background:#000;width:100%}
.video iframe,.video video{position:absolute;inset:0;width:100%;height:100%;border:0}
.vet{padding:14px 0 0;font-size:14px;color:var(--phu)}
.vet a{color:var(--phu)}
.ct{display:grid;grid-template-columns:1fr;gap:22px;padding:26px 0 8px}
.ct figure{margin:0;border-radius:20px;overflow:hidden;background:var(--the);border:1px solid var(--vien);box-shadow:0 10px 28px rgba(27,17,12,.16)}
.ct figure img{display:block;width:100%;height:auto}
.ct h1{font-size:30px;line-height:1.2;margin:0 0 10px}
.chip{display:inline-block;padding:4px 14px;border-radius:999px;background:var(--the);border:1px solid var(--vien);font-size:14px;margin:0 6px 8px 0}
.chip.dam{background:var(--nut);border-color:var(--nut);color:var(--nut-chu);font-weight:700}
.xacthuc{margin:10px 0 4px;padding:12px 14px;border-radius:12px;background:var(--the);border:1px solid var(--vien);border-left:5px solid var(--vang);font-size:15px}
.xacthuc b{color:var(--nhan)}
.bang{margin:18px 0 0;border:1px solid var(--vien);border-radius:14px;overflow:hidden;background:var(--the)}
.bang div{padding:11px 16px;border-top:1px solid var(--vien)}
.bang div:first-child{border-top:0}
.bang dt{font-size:12px;letter-spacing:.8px;text-transform:uppercase;color:var(--phu)}
.bang dd{margin:2px 0 0}
.buoc{list-style:none;margin:0;padding:0;counter-reset:b;display:grid;gap:12px}
.buoc li{counter-increment:b;display:flex;gap:14px;align-items:flex-start;background:var(--the);border:1px solid var(--vien);border-radius:14px;padding:14px 16px}
.buoc li:before{content:counter(b);flex:none;width:34px;height:34px;border-radius:50%;background:var(--nut);color:var(--nut-chu);font:700 17px/34px "Playfair Display",Georgia,serif;text-align:center}
.duongdan{font-size:14px;color:var(--phu);padding-top:16px}
.duongdan a{color:var(--phu)}
.gh{display:block;text-decoration:none;color:inherit;border:1px solid var(--vien);border-radius:18px;overflow:hidden;background:var(--the);box-shadow:0 6px 18px rgba(27,17,12,.1)}
.gh .bia{height:150px;background:var(--ca)}
.gh .bia img{width:100%;height:100%;object-fit:cover;display:block;opacity:.85}
.gh .tt{display:flex;gap:14px;align-items:center;padding:0 16px 16px;margin-top:-30px}
.gh .tt img{width:64px;height:64px;border-radius:50%;object-fit:cover;border:3px solid var(--vang);background:#fff;flex:none}
.gh .tt div{padding-top:30px}
.gh b{display:block;font-family:"Playfair Display",Georgia,serif;font-size:19px;line-height:1.2}
.gh span{font-size:14px;color:var(--phu)}
.chan{background:var(--ca);color:rgba(246,236,219,.8);padding:26px 0 34px;font-size:13px;border-top:2px solid var(--vang)}
.chan a{color:var(--vang)}
@media (min-width:720px){
.hero{min-height:520px}.hero h1{font-size:62px}.hero .kh{font-size:24px}
.mach{grid-template-columns:repeat(3,1fr)}
.luoi{grid-template-columns:repeat(3,1fr)}
.khung-video{flex-direction:row;justify-content:center;gap:56px}
.khung-video .nd{max-width:360px}
.ct{grid-template-columns:1fr 1fr;align-items:start;gap:40px}
.ct figure{position:sticky;top:84px}
h2{font-size:36px}
}
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


def video_dt(url, goc, tieu_de):
    """Khung điện thoại dọc cho video của cơ sở. url: link YouTube, hoặc đường dẫn .mp4 trong kho (hay https)."""
    m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})", url)
    if m:
        return '<div class="dt"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="%s" loading="lazy" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe></div>' % (m.group(1), e(tieu_de))
    if url.lower().endswith((".mp4", ".webm", ".mov")):
        src = url if url.startswith("http") else goc + url
        return '<div class="dt"><video controls preload="metadata" playsinline src="%s#t=0.1"></video></div>' % e(src)
    return '<div class="nut"><a href="%s" rel="noopener">Xem video</a></div>' % e(url)


def khoi_video(c, url, goc, nhan):
    if not url:
        return ""
    return ('<section class="dem" id="video"><div class="w khung-video"><div class="nd"><h2>%s</h2><p class="phude">%s</p></div>%s</div></section>'
            % (e(nhan), e(c["khau_hieu"] or c["ten"]), video_dt(url, goc, nhan)))


def theme(c):
    return ("<style>:root{--nhan:%s;--nut:%s}@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--nhan:%s}}</style>\n"
            % (c["mau"], c["mau"], c["mau_toi"]))


def khung(goc, tieu_de, mo_ta, anh_og, dau, than, c=None, ld="", url=""):
    o = ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
         '<meta name="theme-color" content="#1b110c">\n<title>%s</title>\n<meta name="description" content="%s">\n'
         '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website">'
         '<meta property="og:image" content="%s"><meta property="og:url" content="%s">\n'
         '<link rel="stylesheet" href="%sstyle.css">\n%s%s</head><body>\n'
         % (e(tieu_de), e(mo_ta), e(tieu_de), e(mo_ta), e(anh_og), e(url), goc, theme(c or NT), ld))
    o += dau + "\n" + than
    nguoi = ("<p>%s<br>%s</p>" % (e(c["cong_ty"]), e(c["dia_chi"]))) if c else ""
    o += ('<footer class="chan"><div class="w">%s<p>Thông tin sản phẩm do cơ sở cung cấp. Ngày sản xuất xem trên bao bì.<br>'
          '<a href="%s">%s</a> - mỗi cơ sở một gian hàng thương hiệu.</p></div></footer>\n</body></html>\n' % (nguoi, goc or "./", e(NT["ten"])))
    return o


def dau_co_so(c, goc):
    return ('<header class="dau"><div class="w"><a href="%s%s/"><img src="%s%s" alt=""><div><b class="serif">%s</b><span>%s</span></div></a>'
            '<a class="nt" href="%s">%s</a></div></header>' % (goc, c["slug"], goc, ra(c["slug"], c["logo"]), e(c["ten"]), e(c["nganh"]), goc or "./", e(NT["ten_ngan"])))


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
    return ('<section class="dem" id="lien-he"><div class="w"><h2>Liên hệ</h2><p class="phude">%s</p><div class="nut">%s</div></div></section>'
            % (e(c["dia_chi"]), n))


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
    t = '<div class="w"><div class="duongdan"><a href="%s">%s</a> &rsaquo; <a href="%s%s/">%s</a></div><div class="ct">' % (goc, e(NT["ten_ngan"]), goc, s, e(c["ten"]))
    t += '<figure><img src="%s%s" alt="%s"></figure><div>' % (goc, ra(s, d["anh"]), e(ten))
    t += '<h1>%s</h1><span class="chip dam">%s</span><span class="chip">%s</span><span class="chip">Mã vạch %s</span>' % (e(d["ten"]), kl(sp), e(d["dang"]), sp["gtin"])
    t += '<p>%s</p>' % e(d["gioi_thieu"])
    t += '<div class="xacthuc"><b>Sản phẩm chính hãng %s.</b> Mã GTIN %s đã đăng ký tại Trung tâm Mã số mã vạch quốc gia (GS1 Việt Nam).</div>' % (e(c["ten"]), sp["gtin"])
    t += '<div class="nut"><a href="%s%s/">Vào gian hàng %s</a></div>' % (goc, s, e(c["ten"]))
    t += '<dl class="bang"><div><dt>Thành phần</dt><dd>%s</dd></div><div><dt>Khối lượng tịnh</dt><dd>%s</dd></div>' % (e(d["thanh_phan"]), kl(sp))
    if d.get("do_am"):
        t += '<div><dt>Độ ẩm</dt><dd>%s</dd></div>' % e(d["do_am"])
    t += '<div><dt>Hạn sử dụng</dt><dd>%s</dd></div><div><dt>Hướng dẫn bảo quản</dt><dd>%s</dd></div><div><dt>Cảnh báo</dt><dd>%s</dd></div>' % (e(c["han_dung"]), e(c["bao_quan"]), e(c["canh_bao"]))
    t += '<div><dt>Nhà sản xuất</dt><dd>%s<br>%s</dd></div></dl></div></div>' % (e(c["cong_ty"]), e(c["dia_chi"]))
    if d.get("cach_pha"):
        t += '<h2 class="serif" style="margin-top:34px">Cách pha chế (phin)</h2><ol class="buoc">%s</ol>' % "".join("<li>%s</li>" % e(b) for b in d["cach_pha"])
    t += '</div>'
    t += '<div style="height:36px"></div>'
    t += khoi_video(c, sp.get("video") or c.get("video_gioi_thieu"), goc, "Video %s" % c["ten"])
    khac = [x for x in c["san_pham"] if x["gtin"] != sp["gtin"]]
    if khac:
        t += '<section class="moi"><div class="w"><h2>Sản phẩm khác của %s</h2><div class="luoi" style="margin-top:16px">%s</div></div></section>' % (e(c["ten"]), "".join(
            '<div class="sp"><a href="../%s/"><img src="%s%s" alt="" loading="lazy"></a><div class="nd"><h3>%s</h3><span class="d">%s</span><div class="kl"><a href="../%s/">%s</a></div></div></div>' % (
                x["gtin"], goc, ra(s, c["dong"][x["dong"]]["anh"]), e(c["dong"][x["dong"]]["ten_ngan"]), e(c["dong"][x["dong"]]["dang"]), x["gtin"], kl(x)) for x in khac))
    t += lien_he(c)
    return khung(goc, ten + " | " + c["ten"], d["gioi_thieu"], tuyet_doi(ra(s, d["anh"])), dau_co_so(c, goc), t, c, ld, url)


def trang_co_so(c):
    goc = "../"
    s = c["slug"]
    t = '<section class="hero"><img src="%s%s" alt=""><div class="w"><span class="tag">%s</span><h1>%s</h1><p class="kh">%s</p>' % (goc, ra(s, c["anh_bia"]), e(c["nganh"]), e(c["ten"]), e(c.get("khau_hieu", "")))
    t += '<div class="hang"><a class="btn vang" href="#san-pham">Xem sản phẩm</a>%s<a class="btn vien" href="#lien-he">Liên hệ</a></div></div></section>' % (
        '<a class="btn vien" href="#video">Xem video</a>' if c.get("video_gioi_thieu") else "")
    if c.get("diem_manh"):
        t += '<div class="w mach">%s</div>' % "".join("<div><b>%s</b><span>%s</span></div>" % (e(x["t"]), e(x["m"])) for x in c["diem_manh"])
    t += '<section class="moi" id="san-pham"><div class="w"><h2>Sản phẩm</h2><p class="phude">Chọn quy cách để xem thông tin chi tiết.</p><div class="luoi">'
    for k, d in c["dong"].items():
        sps = [x for x in c["san_pham"] if x["dong"] == k]
        if not sps:
            continue
        t += '<div class="sp"><a href="%s01/%s/"><img src="%s%s" alt="%s" loading="lazy"></a><div class="nd"><h3>%s</h3><span class="d">%s</span><div class="kl">%s</div></div></div>' % (
            goc, sps[0]["gtin"], goc, ra(s, d["anh"]), e(d["ten"]), e(d["ten"]), e(d["dang"]),
            "".join('<a href="%s01/%s/">%s</a>' % (goc, x["gtin"], kl(x)) for x in sps))
    t += '</div></div></section>'
    t += khoi_video(c, c.get("video_gioi_thieu"), goc, "Xem %s qua video" % c["ten"])
    t += '<section class="moi"><div class="w"><h2>Về %s</h2><p>%s</p></div></section>' % (e(c["ten"]), e(c["gioi_thieu"]))
    t += lien_he(c)
    return khung(goc, c["ten"] + " | " + NT["ten"], c["gioi_thieu"], tuyet_doi(ra(s, c["anh_bia"])), dau_co_so(c, goc), t, c, "", tuyet_doi(s + "/"))


def trang_chu():
    d = '<header class="dau"><div class="w"><a href="./"><div><b class="serif">%s</b><span>Quét mã trên bao bì để xem thông tin sản phẩm</span></div></a></div></header>' % e(NT["ten"])
    t = '<section class="hero" style="min-height:300px"><div class="w"><span class="tag">Gian hàng thương hiệu</span><h1 style="font-size:40px">%s</h1><p class="kh" style="color:var(--kem);font-family:system-ui,sans-serif;font-size:17px">%s</p></div></section>' % (e(NT["ten"]), e(NT["mo_ta"]))
    t += '<section class="moi"><div class="w"><h2>Các gian hàng</h2><p class="phude">Chọn một gian hàng để xem sản phẩm.</p><div class="luoi" style="grid-template-columns:1fr">'
    for c in COSO.values():
        t += '<a class="gh" href="%s/"><div class="bia"><img src="%s" alt=""></div><div class="tt"><img src="%s" alt=""><div><b>%s</b><span>%s - %d sản phẩm</span></div></div></a>' % (
            c["slug"], ra(c["slug"], c["anh_bia"]), ra(c["slug"], c["logo"]), e(c["ten"]), e(c["nganh"]), len(c["san_pham"]))
    t += '</div></div></section>'
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
        v = c.get("video_gioi_thieu", "")
        if v and not v.startswith("http"):
            assert os.path.exists(os.path.join(GOC, v)), "thieu video: " + v
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
