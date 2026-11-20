# -*- coding: utf-8 -*-
"""Tạo mã QR (PNG) cho các sản phẩm của một cơ sở, trỏ về trang sản phẩm trong gian hàng.
Cần: python -m pip install segno
Chạy:  python tao_qr.py <slug> <thư mục ra>
Ra:    QR <GTIN13> <tên không dấu> <khối lượng>g.png  (nền trắng, viền 4 ô, mỗi ô 12 điểm, sửa lỗi mức M)
Địa chỉ lấy từ danh_sach_ma.json do tao_trang.py sinh: đổi địa chỉ gốc thì chạy lại tao_trang.py trước.
"""
import json
import os
import sys
import unicodedata

import segno

GOC = os.path.dirname(os.path.abspath(__file__))


def khong_dau(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    slug, ra = argv
    cs = json.load(open(os.path.join(GOC, "co_so", slug, "co_so.json"), encoding="utf-8"))
    ma = json.load(open(os.path.join(GOC, "danh_sach_ma.json"), encoding="utf-8"))
    os.makedirs(ra, exist_ok=True)
    for sp in cs["san_pham"]:
        url = ma[sp["gtin"]]["url"]
        ten = khong_dau(cs["dong"][sp["dong"]]["ten_ngan"]).replace("/", " ")
        f = os.path.join(ra, "QR %s %s %dg.png" % (sp["gtin"], ten, sp["kl"]))
        segno.make(url, error="m").save(f, scale=12, border=4)
        print(sp["gtin"], url, "->", f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
