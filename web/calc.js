// Aviateka calculators — same formulas as mcp/calc.py
const CALC = (() => {
  const R = 287.053, G = 9.80665, OZ = 35.27396, FT2 = 10.76391;
  // U.S. Standard Atmosphere 1976 to 86 km, geopotential altitude — same as calc.py
  const LAYERS = [[0, 288.15, -0.0065], [11000, 216.65, 0], [20000, 216.65, 0.001], [32000, 228.65, 0.0028],
    [47000, 270.65, 0], [51000, 270.65, -0.0028], [71000, 214.65, -0.002]], RE = 6356766;
  const lp = (hb, tb, L, pb, h) => L === 0 ? pb * Math.exp(-G * (h - hb) / (R * tb)) : pb * (tb / (tb + L * (h - hb))) ** (G / (R * L));
  const PB = [101325];
  for (let i = 1; i < LAYERS.length; i++) PB.push(lp(...LAYERS[i - 1], PB[i - 1], LAYERS[i][0]));
  const geopot = z => RE * z / (RE + z);
  function atm(h, dT = 0) {
    if (!(h >= -500 && h <= 84853)) throw new Error('altitude');
    let i = 0; for (let k = 0; k < LAYERS.length; k++) if (h >= LAYERS[k][0]) i = k;
    const [hb, tb, L] = LAYERS[i], Ts = tb + L * (h - hb), p = lp(hb, tb, L, PB[i], h);
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
  // Lighter than air: same model as calc.py buoyancy() — gas pressure equals ambient, dry air
  const RU = 8.314462618, GASES = { helium: 4.002602e-3, hydrogen: 2.01588e-3, hot_air: null };
  function lift(gas, V, tg, purity, m, h, tAmb) {
    if (!(gas in GASES)) throw new Error('input');
    const dT = isFinite(tAmb) ? tAmb + 273.15 - atm(h).T : 0, s = atm(h, dT), rhoA = s.p / (R * s.T);
    let Tg, rhoG;
    if (gas === 'hot_air') { Tg = (isFinite(tg) ? tg : 100) + 273.15; if (!(Tg > s.T)) throw new Error('cold'); rhoG = s.p / (R * Tg); }
    else {
      Tg = isFinite(tg) ? tg + 273.15 : s.T; const pu = isFinite(purity) ? purity : 1;
      if (!(Tg > 0) || !(pu > 0 && pu <= 1)) throw new Error('input');
      rhoG = pu * s.p * GASES[gas] / (RU * Tg) + (1 - pu) * s.p / (R * Tg);
    }
    const k = rhoA - rhoG; if (!(k > 0)) throw new Error('nolift');
    const out = { rhoA, rhoG, k, Ta: s.T - 273.15 };
    if (V > 0) Object.assign(out, { gross: V * k, gasM: V * rhoG, net: m >= 0 ? V * k - m : NaN });
    if (m > 0) { const Vn = m / k; Object.assign(out, { Vn, Dn: Math.cbrt(6 * Vn / Math.PI) }); }
    return out;
  }
  // Rotor hover by momentum theory with figure of merit — same as calc.py rotor_hover()
  function hover(m, D, n, fm, h, eta, wh, usable, dl = 0) {
    if (!(m > 0) || !(D > 0) || !(n >= 1) || !(fm > 0 && fm <= 1) || !(dl >= 0 && dl < 0.5)) throw new Error('input');
    const rho = atm(h).rho, T = m * G / n / (1 - dl), A = Math.PI * D * D / 4, vi = Math.sqrt(T / (2 * rho * A));
    const Pi = T * vi, Ps = Pi / fm, Pt = Ps * n, out = { T, Tg: T / G * 1000, DL: T / A, vi, Pi, Ps, Pt, gW: m * 1000 / Pt };
    out.Pe = eta > 0 && eta <= 1 ? Pt / eta : NaN;
    const draw = isFinite(out.Pe) ? out.Pe : Pt;
    out.tmin = wh > 0 ? wh * (usable > 0 && usable <= 1 ? usable : 1) / draw * 60 : NaN;
    return out;
  }
  // Rocket: ideal rocket equation — same as calc.py rocket_delta_v()
  function rocket(isp, m0, mf, T) {
    if (!(isp > 0) || !(m0 > 0) || !(mf > 0 && mf < m0)) throw new Error('input');
    const ve = isp * G, prop = m0 - mf, out = { ve, prop, mr: m0 / mf, dv: ve * Math.log(m0 / mf) };
    if (T > 0) { const md = T / ve; Object.assign(out, { tw0: T / (m0 * G), tw1: T / (mf * G), md, tb: prop / md }); }
    return out;
  }
  // Entry heating: Sutton–Graves, Earth air, geometric altitude — same as calc.py entry_heating()
  function entry(V, z, Rn, k = 1.7415e-4) {
    if (!(V > 0) || !(Rn > 0)) throw new Error('input');
    const s = atm(geopot(z)), q = k * Math.sqrt(s.rho / Rn) * V ** 3;
    return { rho: s.rho, M: V / s.a, qdyn: 0.5 * s.rho * V * V, q, qLo: q / k * 1.63e-4, qHi: q / k * 1.83e-4 };
  }
  return { atm, geopot, reMach, stall, loading, froude, cav, CHUTES, chute, GASES, lift, hover, rocket, entry };
})();
if (typeof module !== 'undefined') module.exports = CALC;
