
function qb(a) {
        var b = a.split(".");
        if (4 !== b.length)
            throw Error("Invalid format -- expecting a.b.c.d");
        for (var c = a = 0; c < b.length; ++c) {
            var d = parseInt(b[c], 10);
            if (Number.isNaN(d) || 0 > d || 255 < d)
                throw Error("Each octet must be between 0 and 255");
            a |= d << 8 * (b.length - c - 1);
            a >>>= 0
        }
        return a
    }

function l(a, b) {
        this.key = a;
        this.value = b
    }



var d = '192.168.0.1'
for (var a = "", e = "", h = c.getpackStr(b), m = [], q = [], t = [], k = [], n = 0; n < h.length; n++)
    "new" != h[n].value && -1 == Bb.indexOf(h[n].key) && (-1 != Ib.indexOf(h[n].key) ? q.push(h[n]) : -1 != Cb.indexOf(h[n].key) ? t.push(h[n]) : -1 != Hb.indexOf(h[n].key) ? k.push(h[n]) : m.push(h[n]));
h = "";
for (n = 0; n < q.length; n++)
    h = h + q[n].key.charAt(0) + q[n].value;
q = "";
for (n = 0; n < k.length; n++)
    q = 0 == n ? q + k[n].value : q + "x" + k[n].value;
k = "";
for (n = 0; n < t.length; n++)
    k = 0 == n ? k + t[n].value : k + "x" + t[n].value;
m.push(new l("storeDb",h));
m.push(new l("srcScreenSize",q));
m.push(new l("scrAvailSize",k));
"" != d && m.push(new l("localCode",qb(d)));
e = c.hashAlg(m, a, e);
a = e.key;
e = e.value;
a += "&timestamp=" + (new Date).getTime();