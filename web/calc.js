// Aviateka calculators — same formulas as mcp/calc.py
const CALC = (() => {
  const R = 287.053, G = 9.80665, OZ = 35.27396, FT2 = 10.76391;
  function atm(h, dT = 0) {
    if (!(h >= -500 && h <= 20000)) throw new Error('altitude');
    let Ts, p;
    if (h <= 11000) { Ts = 288.15 - 0.0065 * h; p = 101325 * (Ts / 288.15) ** 5.255877; }
    else { Ts = 216.65; p = 22632.06 * Math.exp(-G * (h - 11000) / (R * 216.65)); }
    const T = Ts + dT, rho = p / (R * T), a = Math.sqrt(1.4 * R * T), mu = 1.458e-6 * T ** 1.5 / (T + 110.4);
    return { T, p, rho, a, mu, nu: mu / rho };
  }
  function reMach(V, c, h, dT) { const s = atm(h, dT); return { re: V * c / s.nu, mach: V / s.a, atm: s }; }
  function stall(m, S, cl, h, dT) { const s = atm(h, dT); const vs = Math.sqrt(2 * m * G / (s.rho * S * cl)); return { vs, rho: s.rho }; }
  const WCL = [[4, 'wcl0'], [7, 'wcl1'], [9, 'wcl2'], [13, 'wcl3'], [25, 'wcl4'], [Infinity, 'wcl5']];
  function loading(m, S) { const w = (m * OZ) / (S * FT2) ** 1.5; return { kgm2: m / S, gdm2: m * 1000 / (S * 100), wcl: w, cls: WCL.find(c => w < c[0])[1] }; }
  function froude(k, m, V, I, rf, rm) {
    const d = rm / rf;
    return { m: m / k ** 3 * d, V: V / Math.sqrt(k), I: I.map(x => x / k ** 5 * d), t: 1 / Math.sqrt(k), f: Math.sqrt(k), re: k ** -1.5 };
  }
  function cav(V, depth, cpmin, tw, salt) {
    if (!(V > 0) || !(depth >= 0) || !(cpmin < 0) || !(tw >= 0 && tw <= 50)) throw new Error('input');
    const rho = salt ? 1025 : 998.2, pv = 610.94 * Math.exp(17.625 * tw / (tw + 243.04));
    const pl = 101325 + rho * G * depth - pv, sigma = pl / (0.5 * rho * V * V), vi = Math.sqrt(pl / (0.5 * rho * -cpmin));
    return { sigma, vi, cav: sigma < -cpmin, pv, rho };
  }
  // Parachute: CD0 on nominal area S0; same table as calc.py (CANOPIES)
  const CHUTES = { flat_circular: [0.75, 0.80], extended_skirt_10: [0.78, 0.87], ringsail: [0.75, 0.90], ringslot: [0.56, 0.65],
    disk_gap_band: [0.52, 0.58], conical_ribbon: [0.50, 0.55], flat_ribbon: [0.45, 0.50], guide_surface_ribbed: [0.28, 0.42] };
  function chute(m, lo, hi, D, Vt, h, dT = 0) {
    if (!(m > 0) || !(lo > 0) || !(hi >= lo)) throw new Error('input');
    const rho = atm(h, dT).rho, w2 = 2 * m * G, cd = (lo + hi) / 2, out = { rho, cd };
    if (D > 0) {
      const S = Math.PI * D * D / 4, v = Math.sqrt(w2 / (rho * cd * S));
      Object.assign(out, { S, v, vLo: Math.sqrt(w2 / (rho * hi * S)), vHi: Math.sqrt(w2 / (rho * lo * S)), E: 0.5 * m * v * v, hEq: v * v / (2 * G) });
    }
    if (Vt > 0) { const Sn = w2 / (rho * cd * Vt * Vt); Object.assign(out, { Sn, Dn: Math.sqrt(4 * Sn / Math.PI) }); }
    return out;
  }
  return { atm, reMach, stall, loading, froude, cav, CHUTES, chute };
})();
if (typeof module !== 'undefined') module.exports = CALC;
