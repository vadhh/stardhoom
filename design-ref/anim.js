// Background: the Gringsing Lidah Api Padma batik as a stipple of dots behind the hero only (it scrolls away with it
// and fades out at its foot; the sections below sit on the flat ground). A port of remotion/src/batikDots.ts (the
// BatikHeroEntrance composition) to WebGL points, so it reacts to the pointer instead of playing a video: the dots wake
// from the flame at the centre outwards over 2 s, then breathe in a seamless 10 s loop (a radial wave, a diagonal
// sheen, the dark fills' inner breath) while the pointer is on the hero, and swell, brighten and lean away round it.
// With no pointer on the hero they dim and still, and nothing draws. The dots are
// img/batik-dots.bin (design-ref/pack_dots.py). Reduced motion and touch screens draw one settled frame, the loop's
// first; elsewhere a button in the hero pauses it. No WebGL or no data: no canvas, the flat ground.
const DOTS_VS = `
attribute vec2 a_xy; attribute float a_r, a_tone, a_flags;
uniform vec2 u_res; uniform vec3 u_ptr; uniform float u_dpr, u_in, u_phase, u_pass, u_lit;
varying float v_a, v_px;
const float SRC_W = 1872.0, SRC_H = 1720.0, MOTIF_X = 0.483, ML = 0.008, MR = 0.992, ZOOM = 1.14, PI = 3.14159265;
const float DIM = 0.45;   // the light with no pointer on the hero (u_lit 0), a share of full (u_lit 1)
float c01(float v) { return clamp(v, 0.0, 1.0); }
void main() {
  float W = u_res.x, H = u_res.y, s = H / SRC_H * ZOOM, tW = SRC_W * s, tH = SRC_H * s, x = a_xy.x;
  // pass 0 is the cloth, 1 and 2 its mirror images through the corner Lidah Api, so wide screens show no seam
  float mx = u_pass < 0.5 ? x : u_pass < 1.5 ? 2.0 * ML - x : 2.0 * MR - x;
  bool seam = (u_pass > 0.5 && u_pass < 1.5 && x <= ML + 0.004) || (u_pass > 1.5 && x >= MR - 0.004);
  vec2 p = vec2(W * 0.5 - MOTIF_X * tW + mx * tW, a_xy.y * tH - H * 105.0 / 1080.0);
  float nx = p.x / W, ny = p.y / H, tone = a_tone;
  bool dark = mod(a_flags, 2.0) > 0.5, hi = a_flags > 1.5;
  float textMask = 1.0 - 0.52 * c01((ny - 0.57) / 0.26);   // the name and lead along the bottom stay readable
  float edge = c01((abs(nx - 0.5) * 2.0 - 0.55) / 0.45);
  float baseA = tone * (0.34 + 0.66 * c01(ny / 0.085)) * textMask * (1.0 - 0.36 * pow(edge, 1.5));
  float baseR = max(0.85, a_r * 0.01 * max(tW, tH) * (0.82 + 0.18 * tone));
  float dist = length((p - vec2(W * 0.5, H * 0.51)) / vec2(W * 0.52, H * 0.58));
  float reveal = c01(dist / 1.22) * 0.78 + (1.0 - tone) * 0.22;   // bright crests first, from the flame outwards
  float wake = u_in >= 0.999 ? 1.0 : c01((u_in - reveal * 0.8) / 0.2);
  float wave = sin(u_phase - dist * PI * 2.8), sheen = sin(u_phase - (nx * 0.72 + ny * 0.45) * 2.0 * PI + 0.85);
  float breath = dark ? sin(u_phase + dist * 2.2 - ny * 5.0) * 0.08 : 0.0;
  float damp = 1.0 - 0.55 * c01((ny - 0.56) / 0.25);
  // intensity 0.78: Remotion's BatikHeroWithOverlay, the composition made for the hero's text on top
  // the pointer: within 180px the dots swell, brighten and lean away from it, damped over the text like the loop
  vec2 d = p - u_ptr.xy;
  float pl = length(d), f = u_ptr.z * damp * textMask * pow(c01(1.0 - pl / 180.0), 2.0);
  if (pl > 0.5) p += d / pl * 12.0 * f;
  float r = baseR * (1.0 + damp * ((hi ? 0.13 : 0.09) * wave + 0.05 * sheen + breath)) * (0.35 + 0.65 * wake) * (1.0 + 0.7 * f);
  v_a = c01(baseA * 0.78 * (1.0 + damp * (0.13 * wave + 0.07 * sheen + breath * 1.1)) * wake * (1.0 + 0.9 * f)) * mix(DIM, 1.0, u_lit);
  v_px = 2.0 * r * u_dpr;
  bool off = seam || wake <= 0.01 || r <= 0.2 || v_a <= 0.02;
  gl_PointSize = off ? 0.0 : v_px;
  gl_Position = off ? vec4(2.0, 2.0, 2.0, 1.0) : vec4(p.x / W * 2.0 - 1.0, 1.0 - p.y / H * 2.0, 0.0, 1.0);
}`;
const DOTS_FS = `
precision mediump float;
uniform vec3 u_ink; varying float v_a, v_px;
void main() {
  float a = v_a * clamp(v_px * 0.5 - length(gl_PointCoord - 0.5) * v_px + 0.5, 0.0, 1.0);   // a round dot, soft 1px rim
  gl_FragColor = vec4(u_ink * a, a);
}`;
// a linked WebGL program, or undefined (its log warned) when a shader fails to build
function program(gl, vs, fs, name) {
  const p = gl.createProgram();
  [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]].forEach(([type, src]) => {
    const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); gl.attachShader(p, s); });
  gl.linkProgram(p);
  return gl.getProgramParameter(p, gl.LINK_STATUS) ? p : console.warn(name + ":", gl.getProgramInfoLog(p));
}
function waves() {
  const cv = document.querySelector(".bg-waves"), hero = document.querySelector(".hero"), btn = document.querySelector(".bg-pause"),
    gl = cv.getContext("webgl", { antialias: false }), u = {};
  const prog = gl && program(gl, DOTS_VS, DOTS_FS, "batik dots");
  if (!prog) { cv.hidden = true; return { play() {}, stop() {} }; }
  // still until play(): the settled frame where motion never starts, the empty first frame of the entrance where it will
  let W, H, dpr, n = 0, t = 0, lit = 1, since = 0, last = -1, paused = false, ptr = [-1e4, -1e4, 0], aim = [-1e4, -1e4, 0],
    still = matchMedia("(prefers-reduced-motion: reduce), (pointer: coarse)").matches;
  gl.useProgram(prog);
  ["u_res", "u_ptr", "u_dpr", "u_in", "u_phase", "u_pass", "u_lit", "u_ink"].forEach((k) => u[k] = gl.getUniformLocation(prog, k));
  gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);   // premultiplied, over the page's own ground
  const ink = getComputedStyle(document.documentElement).getPropertyValue("--text").trim();
  gl.uniform3fv(u.u_ink, [1, 3, 5].map((i) => parseInt(ink.slice(i, i + 2), 16) / 255));
  // the entrance's easing in Remotion, cubic-bezier(.32, .08, .45, 1), solved for x by bisection
  const ease = (x) => {
    const b = (s, p1, p2) => 3 * p1 * s * (1 - s) * (1 - s) + 3 * p2 * s * s * (1 - s) + s * s * s;
    let lo = 0, hi = 1, s = x;
    for (let i = 0; i < 24; i++) { s = (lo + hi) / 2; if (b(s, 0.32, 0.45) < x) lo = s; else hi = s; }
    return b(s, 0.08, 1);
  };
  const frame = () => {
    if (n <= 0) return;
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform2f(u.u_res, W, H); gl.uniform1f(u.u_dpr, dpr); gl.uniform3fv(u.u_ptr, ptr);
    gl.uniform1f(u.u_in, still ? 1 : ease(Math.min(t / 2, 1))); gl.uniform1f(u.u_lit, still ? 1 : lit);
    gl.uniform1f(u.u_phase, still ? 0 : ((t - 2) % 10) / 10 * 2 * Math.PI);   // a 2 s entrance, then the 10 s loop
    for (let pass = 0; pass < 3; pass++) { gl.uniform1f(u.u_pass, pass); gl.drawArrays(gl.POINTS, 0, n); }
  };
  const size = () => {
    dpr = Math.min(devicePixelRatio || 1, 2); W = cv.clientWidth; H = hero.offsetHeight;
    cv.style.height = H + "px"; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); gl.viewport(0, 0, cv.width, cv.height);
  };
  fetch("img/batik-dots.bin").then((r) => r.ok ? r.arrayBuffer() : Promise.reject(r.status)).then((buf) => {
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, buf, gl.STATIC_DRAW);
    // 8 bytes a dot (design-ref/pack_dots.py): u16 x, y and radius, u8 tone and flags
    [["a_xy", 2, gl.UNSIGNED_SHORT, true, 0], ["a_r", 1, gl.UNSIGNED_SHORT, true, 4], ["a_tone", 1, gl.UNSIGNED_BYTE, true, 6],
      ["a_flags", 1, gl.UNSIGNED_BYTE, false, 7]].forEach(([name, k, type, norm, at]) => {
      const loc = gl.getAttribLocation(prog, name); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, k, type, norm, 8, at); });
    n = buf.byteLength / 8; frame();
  }).catch(() => { n = -1; cv.hidden = btn.hidden = true; hint(); });
  // the "vadh" hint blinks first once the dots have entered and dimmed (CSS, .hero[data-hint]); a pause or no dots
  // let it go at once
  const hint = () => { if (hero.dataset.hint === "wait") hero.dataset.hint = "go"; };
  // every frame of the ticker; nothing draws while the tab is hidden, the hero is scrolled away or the viewer has
  // paused it. The clock holds at 0 until the dots arrive, so a slow load still gets its entrance
  const tick = (time) => {
    if (document.hidden || paused || n <= 0 || scrollY > H) { last = -1; return; }
    const dt = last < 0 ? 0 : Math.min(time - last, 0.1), k = 1 - Math.exp(-dt * 10);
    last = time;
    ptr[0] += (aim[0] - ptr[0]) * k; ptr[1] += (aim[1] - ptr[1]) * k; ptr[2] += (aim[2] - ptr[2]) * k / 2;
    // after the entrance the light follows the pointer: up and breathing while it is on the hero, down to DIM and
    // still once it leaves (the loop's clock runs at the light's pace), and then nothing draws until it comes back
    if (t >= 2) lit += (aim[2] - lit) * (1 - Math.exp(-dt * 2.5));
    t += t < 2 ? dt : dt * lit;
    if (t >= 2 && (since += dt) >= 1.5) hint();   // the dim is all the way down by then (lit under 3%)
    if (t >= 2 && !aim[2] && lit + ptr[2] < 1e-3) return;
    frame();
  };
  // the canvas sits at the top of the page; the lens appears where the pointer comes in, not swept in from afar
  const point = (e) => { if (e.pointerType === "touch") return;
    aim[0] = e.clientX; aim[1] = e.clientY + scrollY; aim[2] = aim[1] < H ? 1 : 0;
    if (ptr[2] < 0.01) { ptr[0] = aim[0]; ptr[1] = aim[1]; } };
  const leave = (e) => { if (!e.relatedTarget) aim[2] = 0; };   // the pointer left the window
  const toggle = () => { paused = !paused; btn.setAttribute("aria-pressed", paused); hint(); };
  const resize = () => { size(); frame(); };
  size(); addEventListener("resize", resize); new ResizeObserver(resize).observe(hero);
  return {
    play() { if (n < 0 || matchMedia("(pointer: coarse)").matches) return;   // a phone or tablet keeps the still
      still = false; t = 0; lit = 1; since = 0; last = -1; btn.hidden = false; hero.dataset.hint = "wait";
      gsap.ticker.add(tick); addEventListener("pointermove", point); document.addEventListener("pointerout", leave);
      btn.addEventListener("click", toggle); },
    stop() { gsap.ticker.remove(tick); removeEventListener("pointermove", point); document.removeEventListener("pointerout", leave);
      btn.removeEventListener("click", toggle); btn.hidden = true; paused = false; btn.setAttribute("aria-pressed", false);
      delete hero.dataset.hint;
      still = true; ptr = [-1e4, -1e4, 0]; aim = [-1e4, -1e4, 0]; frame(); },
  };
}

// The page closes on a flower in glass tiles: past the footer, a screen of a reel's halftone flower (64 x 36 squares,
// 79 frames), traced by design-ref/trace_flower.py into img/footer-flower.png and drawn as frosted glass in the cyan,
// blue and green of a glass-tile reference, on the page's ground. A tile's brightness and colour follow the
// reel's tone (tone()), so the petals read; the empty ones are faint rims, and the tone glows through the gaps.
const FULL_VS = `attribute vec2 a_p; void main() { gl_Position = vec4(a_p, 0.0, 1.0); }`;
const FLOWER_FS = `
precision highp float;
uniform sampler2D u_data; uniform vec2 u_res, u_org; uniform float u_pitch, u_frame, u_time;
const vec2 GRID = vec2(64.0, 36.0), SHEET = vec2(512.0, 360.0);
vec2 at(vec2 c, float k) {                     // cell c in frame k: (the reel's square side / 16 px, filled 0 or 1)
  if (c.x < 0.0 || c.y < 0.0 || c.x >= GRID.x || c.y >= GRID.y) return vec2(0.0);
  vec4 t = texture2D(u_data, (vec2(mod(k, 8.0), floor(k / 8.0)) * GRID + c + 0.5) / SHEET);
  return vec2(t.r * 255.0 / 256.0, t.g);
}
vec2 cell(vec2 c) { float k = floor(u_frame); return mix(at(c, k), at(c, min(k + 1.0, 78.0)), u_frame - k); }
// the reel's brightness: its square's area, so an 8 px square is 0.12 and a 16 px one 1; a hollow square is 0
float tone(vec2 v) { return v.y * clamp((v.x * v.x - 0.15) / 0.85, 0.0, 1.0); }
float box(vec2 q, float h, float r) { vec2 d = abs(q) - h + r; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0) - r; }
vec3 tint(vec2 uv) {                           // the reference's backdrop: ice at the top, cyan, blue low left, green low right
  vec3 ice = vec3(0.80, 0.95, 0.98), cyan = vec3(0.42, 0.84, 0.92), blue = vec3(0.48, 0.68, 0.95), green = vec3(0.36, 0.80, 0.52);
  vec3 c = mix(cyan, blue, smoothstep(0.35, 0.95, uv.y) * smoothstep(0.75, 0.15, uv.x + 0.15 * sin(u_time * 0.21)));
  c = mix(c, green, smoothstep(0.45, 1.0, uv.y + 0.2 * sin(uv.x * 3.0 + u_time * 0.13)) * smoothstep(0.3, 0.7, uv.x));
  return mix(c, ice, smoothstep(0.4, 0.0, uv.y) * 0.6);
}
void main() {
  vec2 p = vec2(gl_FragCoord.x, u_res.y - gl_FragCoord.y), g = (p - u_org) / u_pitch, c = floor(g), q = g - c - 0.5;
  vec2 v = cell(c), b = floor(g - 0.5), f = g - 0.5 - b;
  // the tone as a smooth field, bilinear between cell centres: the backdrop that glows through the gaps
  float field = mix(mix(tone(cell(b)), tone(cell(b + vec2(1, 0))), f.x), mix(tone(cell(b + vec2(0, 1))), tone(cell(b + vec2(1, 1))), f.x), f.y);
  float px = 1.0 / u_pitch, lit = v.y, k = tone(v), h = 0.46, a = mix(0.035, 0.2 + 0.8 * k, lit);
  float d = box(q, h, h * 0.3), inside = smoothstep(0.6 * px, -0.6 * px, d), e = 1.0 - clamp(-d / h, 0.0, 1.0);
  // the colour follows the shading, so the petals read: deep blue where the reel is dim, cyan, ice where it is brightest;
  // the reference's backdrop tints it a third of the way
  vec3 col = mix(mix(vec3(0.20, 0.38, 0.66), vec3(0.42, 0.84, 0.92), smoothstep(0.0, 0.55, k)), vec3(0.90, 0.98, 1.0), smoothstep(0.55, 1.0, k));
  col = mix(col, tint(p / u_res), 0.35);
  float frost = 0.58 + 0.4 * e * e * e + 0.16 * smoothstep(0.7, -0.9, (q.x + q.y * 1.6) / h);   // bright at the rim, a sheen
  float rim = 1.0 - smoothstep(0.0, 1.4 * px, abs(d + 0.9 * px)), side = clamp(0.55 - (q.x + q.y) / h * 0.45, 0.0, 1.0);
  vec3 tile = col * frost * a + rim * mix(0.05, 0.6, side * side) * mix(0.25, 1.0, a) * mix(0.35, 1.0, lit) * mix(col, vec3(1.0), 0.55);
  vec3 o = vec3(20.0 / 255.0) + col * (exp(-max(d, 0.0) * 14.0) * k * 0.25 + field * 0.2);   // halo, backdrop
  gl_FragColor = vec4(mix(o, o * (1.0 - a) + tile, inside), 1.0);
}`;
// The frames play forth and back on a 14 s ease: the reel is a one-way 5 s move, so a loop of it would jump. The sheet
// loads near the screen; motion plays it until the viewer pauses it, reduced motion draws its first frame still, and no
// JS, no WebGL or a failed load keep the poster, that same frame rendered.
function endFlower() {
  const box = document.querySelector(".flower-end"), cv = box.querySelector("canvas"), btn = box.querySelector(".bg-pause"),
    gl = cv.getContext("webgl", { antialias: false }), u = {};
  const prog = gl && program(gl, FULL_VS, FLOWER_FS, "flower");
  if (!prog) { cv.hidden = true; return { play() {}, stop() {} }; }
  let sheet = null, ready = false, near = false, paused = false, t = 0, last = -1;
  gl.useProgram(prog);
  ["u_data", "u_res", "u_org", "u_pitch", "u_frame", "u_time"].forEach((k) => u[k] = gl.getUniformLocation(prog, k));
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);   // one triangle over the canvas
  const loc = gl.getAttribLocation(prog, "a_p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const draw = () => {
    if (!ready) return;
    const dpr = Math.min(devicePixelRatio || 1, 2), w = Math.round(cv.clientWidth * dpr), h = Math.round(cv.clientHeight * dpr);
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; gl.viewport(0, 0, w, h); }
    // the reel's grid covers the screen; a tall one shows its middle 30 columns, and the empty tiles run on above and below
    const pitch = Math.min(Math.max(w / 64, h / 36), w / 30);
    gl.uniform2f(u.u_res, w, h); gl.uniform2f(u.u_org, (w - 64 * pitch) / 2, (h - 36 * pitch) / 2); gl.uniform1f(u.u_pitch, pitch);
    gl.uniform1f(u.u_frame, 39 * (1 - Math.cos(t / 14 * 2 * Math.PI))); gl.uniform1f(u.u_time, t);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  };
  const load = () => {
    sheet = new Image();
    sheet.onload = () => {
      gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, sheet);
      [gl.TEXTURE_MIN_FILTER, gl.TEXTURE_MAG_FILTER].forEach((k) => gl.texParameteri(gl.TEXTURE_2D, k, gl.NEAREST));
      [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach((k) => gl.texParameteri(gl.TEXTURE_2D, k, gl.CLAMP_TO_EDGE));
      ready = true; draw();
    };
    sheet.onerror = () => { cv.hidden = btn.hidden = true; };
    sheet.src = cv.dataset.src;
  };
  new IntersectionObserver(([en]) => { near = en.isIntersecting; if (near && !sheet) load(); }, { rootMargin: "50% 0px" }).observe(box);
  addEventListener("resize", draw);
  // every frame of the ticker while the screen is near, the tab shown and the loop not paused
  const tick = (time) => {
    if (!near || paused || !ready || document.hidden) { last = -1; return; }
    t += last < 0 ? 0 : Math.min(time - last, 0.1); last = time; draw();
  };
  const toggle = () => { paused = !paused; btn.setAttribute("aria-pressed", paused); };
  return {
    play() { btn.hidden = cv.hidden; gsap.ticker.add(tick); btn.addEventListener("click", toggle); },
    stop() { gsap.ticker.remove(tick); btn.removeEventListener("click", toggle); btn.hidden = true; paused = false;
      btn.setAttribute("aria-pressed", false); t = 0; last = -1; draw(); },
  };
}

// GitHub card on "vadh" (CSS shows and hides it): placed under the link each time it opens, refreshed from the API
// the first time. Delegated listeners, because SplitText's autoSplit rebuilds the h1's contents on resize.
function ghCard() {
  const card = document.getElementById("gh-card");
  let fetched = false;
  const open = (e) => {
    const a = e.target.closest(".gh");
    if (!a || a.contains(e.relatedTarget)) return;
    card.classList.remove("off");
    const r = a.getBoundingClientRect(), p = card.offsetParent.getBoundingClientRect();
    card.style.left = Math.max(0, Math.min(r.left - p.left, p.width - card.offsetWidth)) + "px";
    const h = card.offsetHeight, flip = r.top - 10 - h > 0;   // above when it fits: below, it would cover the CTAs
    card.style.top = (flip ? r.top - p.top - 10 - h : r.bottom - p.top + 10) + "px";
    if (fetched) return;
    fetched = true;
    fetch("https://api.github.com/users/vadhh").then((res) => res.ok ? res.json() : {}).then((u) =>
      card.querySelectorAll("[data-k]").forEach((el) => { const v = u[el.dataset.k]; if (v != null && v !== "") el.textContent = v; }))
      .catch(() => {});   // offline or rate-limited: the built-in snapshot stays
  };
  document.addEventListener("pointerover", open);
  document.addEventListener("focusin", open);
  // Escape dismisses it until the pointer or focus comes back to the link
  document.addEventListener("keydown", (e) => e.key === "Escape" && card.classList.add("off"));
  // so does the wheel: the name lifts while the card stays put (not scroll, which focusing the link also fires)
  document.addEventListener("wheel", () => card.classList.add("off"), { passive: true });
}
addEventListener("DOMContentLoaded", ghCard);

addEventListener("DOMContentLoaded", () => document.fonts.ready.then(() => {
  const root = document.documentElement;
  if (!window.gsap) return root.classList.remove("js");
  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin);
  const mm = gsap.matchMedia(), bg = waves(), end = endFlower();
  mm.add("(prefers-reduced-motion: no-preference)", () => {
    bg.play(); end.play();
    const once = { start: "top 85%", once: true }, cleanups = [];

    // snap, on Lenis' wheel input: a swipe glides at once to the next stop in its direction when that stop is at most a
    // screen away (all between already on screen, so the glide skips nothing unseen), and the rest of the swipe, momentum
    // included, is swallowed until the wheel rests 150ms: one swipe, one stop, never pulled back. Further away (inside
    // Work and Experience, taller than a screen) the page scrolls freely. Stops: each section's top and, past the footer,
    // the batik screen's bottom edge twice: at a marker a third down it (its top third showing), then at its foot (the
    // whole cloth). Wheel and trackpad only: touch, keys and anchor jumps scroll as they are
    // ponytail: a new swipe begun while the last one's momentum still runs is swallowed with it; if that bites, treat a
    // rise in |deltaY| as a new swipe
    let held = 0;
    const stops = () => [
      ...[...document.querySelectorAll(".hero, main > section")].map((el) => el.getBoundingClientRect().top + scrollY),
      ...[...document.querySelectorAll(".flower-end .third, .flower-end")].map((el) => el.getBoundingClientRect().bottom + scrollY - innerHeight),
    ];
    const snap = ({ deltaX, deltaY, event }) => {
      if (!event.type.includes("wheel") || event.ctrlKey) return true;   // touch and pinch zoom
      const now = performance.now(), from = lenis.targetScroll, dir = Math.sign(deltaY);
      if (now < held) { held = Math.max(held, now + 150); event.cancelable && event.preventDefault(); return false; }
      // sideways swipes and the 1-3px a resting finger sends scroll as they are
      if (Math.abs(deltaY) < 4 || Math.abs(deltaY) <= Math.abs(deltaX)) return true;
      const ahead = stops().filter((y) => (y - from) * dir >= 1 && (y - from) * dir <= innerHeight);
      if (!ahead.length) return true;
      held = now + 600; event.cancelable && event.preventDefault();
      lenis.scrollTo(dir > 0 ? Math.min(...ahead) : Math.max(...ahead), { duration: 0.6, easing: (t) => 1 - Math.pow(1 - t, 4) });
      return false;
    };
    // smooth scroll, driven by GSAP's ticker so ScrollTrigger stays in sync; anchors glide too
    const lenis = window.Lenis && new Lenis({ autoRaf: false, virtualScroll: snap });
    const raf = (t) => lenis.raf(t * 1000);
    // in-page links glide, then hand focus to the target (Tab carries on from there) and update the hash
    const jump = (e) => {
      const a = e.target.closest('a[href^="#"]'), el = a && document.getElementById(a.hash.slice(1));
      if (!el || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault(); history.pushState(null, "", a.hash);
      lenis.scrollTo(el, { onComplete: () => el.focus({ preventScroll: true }) });
    };
    if (lenis) {
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(raf); gsap.ticker.lagSmoothing(0);
      document.addEventListener("click", jump); cleanups.push(() => document.removeEventListener("click", jump));
    }

    // hero: rules draw down, the name rises letter by letter out of its line mask, then the offer, both paths
    // and the facts row fade up, corner brackets last
    // the CTAs' underlines draw in with them (--u scales .cta::before); .drawing holds off its hover transition meanwhile
    const ctas = gsap.utils.toArray(".paths .cta"), drawn = () => ctas.forEach((el) => el.classList.remove("drawing"));
    ctas.forEach((el) => el.classList.add("drawing")); cleanups.push(drawn);
    gsap.timeline()
      .fromTo(".wrap", { "--rule": 0 }, { "--rule": 1, duration: 1.6, ease: "power2.inOut" }, 0)
      .from(".intro .lead span", { y: 24, autoAlpha: 0, duration: 0.9, stagger: 0.1, ease: "power3.out" }, 0.7)
      .fromTo(ctas, { y: 16, autoAlpha: 0, "--u": 0 },
        { y: 0, autoAlpha: 1, "--u": 1, duration: 0.8, stagger: 0.1, ease: "power3.out", onComplete: drawn }, 0.95)
      .from(".facts > *", { y: 24, autoAlpha: 0, duration: 0.9, stagger: 0.08, ease: "power3.out" }, 1.1)
      .from(".corner", { autoAlpha: 0, scale: 0, duration: 0.5, ease: "back.out(2)" }, 1.5);
    gsap.set(".intro .lead, .paths", { visibility: "visible" });
    // deepSlice off: the default slices the nested "vadh" link and leaves an empty, focusable <a> clone behind.
    // SplitText names the h1 (aria-label) and hides every line and letter from screen readers, the link's line and mask
    // too, which would hide a focusable link: each split gives those back, so only letters stay hidden and the link
    // reads by its own aria-label
    SplitText.create("h1", { type: "lines,chars", mask: "lines", autoSplit: true, deepSlice: false,
      onSplit: (self) => {
        const h1 = self.elements[0];
        for (let el = h1.querySelector(".gh").parentElement; el !== h1; el = el.parentElement) el.removeAttribute("aria-hidden");
        return gsap.from(self.chars, { yPercent: 110, duration: 1.2, stagger: 0.035, delay: 0.15, ease: "expo.out" });
      } });

    // contact bookend: the closing line rises letter by letter like the name when it scrolls in. Its masks get room
    // below for the g's tail (.ln-mask), so it starts deeper (125%, not 110%) to hide the i dots under that room. Once it has played, a re-split on resize makes no new tween.
    let closed = false;
    SplitText.create("#contact-h", { type: "lines,chars", mask: "lines", linesClass: "ln", autoSplit: true,
      onSplit: (self) => closed ? undefined : gsap.from(self.chars, { yPercent: 125, duration: 1.2, stagger: 0.035, ease: "expo.out",
        scrollTrigger: { trigger: "#contact-h", ...once, onEnter: () => closed = true } }) });
    // then the email's underline draws in from the left (--u scales .email::after); .drawing holds off the CSS
    // hover transition so it doesn't chase the tween. clamp(): on tall screens the email never climbs to 85%, so the
    // start is pinned to the page end
    const email = document.querySelector(".email");
    email.classList.add("drawing"); cleanups.push(() => email.classList.remove("drawing"));
    gsap.fromTo(email, { "--u": 0 }, { "--u": 1, duration: 0.9, delay: 0.2, ease: "power3.inOut",
      scrollTrigger: { trigger: email, once: true, start: "clamp(top 85%)" }, onComplete: () => email.classList.remove("drawing") });

    // mono labels and card numbers scramble in
    gsap.utils.toArray(".label, .idx").forEach((el) => gsap.fromTo(el, { autoAlpha: 0 }, {
      autoAlpha: 1, duration: 0.9, ease: "none", scrollTrigger: { trigger: el, ...once },
      scrambleText: { text: el.textContent, chars: el.matches(".idx") ? "0123456789" : "01/_<>", speed: 0.5 } }));

    // work cards: covers wipe up while the image settles, staggered per row. Cards and job rows fade with opacity, not
    // autoAlpha: visibility:hidden would drop their links from the Tab order until they scroll in.
    gsap.set(".card", { opacity: 0, y: 40 });
    gsap.set(".cover", { clipPath: "inset(100% 0% 0% 0%)" });
    gsap.set(".cover img", { scale: 1.15 });
    ScrollTrigger.batch(".card", { ...once, onEnter: (cards) => {
      const covers = cards.map((c) => c.querySelector(".cover"));
      gsap.timeline({ defaults: { stagger: 0.12 } })
        .to(cards, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, 0)
        .to(covers, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.1, ease: "expo.inOut" }, 0)
        .to(covers.map((c) => c.querySelector("img")).filter(Boolean), { scale: 1, duration: 1.4, ease: "expo.out" }, 0);
    } });

    // experience rows slide up
    gsap.set(".job", { opacity: 0, y: 50 });
    ScrollTrigger.batch(".job", { ...once, onEnter: (rows) =>
      gsap.to(rows, { opacity: 1, y: 0, duration: 0.9, stagger: 0.12, ease: "power3.out" }) });

    // numbers in highlights count up from 0 once the line is in view, keeping their decimals, then snap back to the
    // exact text. Nothing is zeroed before the trigger fires, so the real numbers sit in the DOM until then. Only
    // multi-digit numbers count: a single digit would flash false values ("under 0 second", "almost 1x faster").
    const counted = gsap.utils.toArray(".hl").filter((el) => /\d\d/.test(el.textContent)).map((el) => [el, el.textContent]);
    counted.forEach(([el, text]) => {
      const n = { p: 0 };
      const draw = () => el.textContent = text.replace(/\d+(\.\d+)?/g, (m, d) => (m * n.p).toFixed(d ? d.length - 1 : 0));
      gsap.to(n, { p: 1, duration: 1.4, ease: "power2.out", onStart: draw, onUpdate: draw, onComplete: () => el.textContent = text,
        scrollTrigger: { trigger: el, start: "top 90%", once: true } });
    });
    return () => {
      counted.forEach(([el, text]) => el.textContent = text);
      cleanups.forEach((f) => f());
      bg.stop(); end.stop();
      if (lenis) { gsap.ticker.remove(raf); lenis.destroy(); }
    };
  });
  // parallax, desktop only: the name lifts out a little faster than the page as the hero scrolls away (below 1024px
  // it sits right under the nav, so the distance is 0). The page does it in CSS (h1's scroll-driven `lift`); this
  // scrub is the fallback where scroll-driven animations aren't supported. Not a width query: a context created
  // during a resize refresh makes ScrollTrigger skip restoring the scroll position, and the page jumps to the top.
  if (!CSS.supports("(animation-timeline: view()) and (animation-range: entry)")) mm.add("(prefers-reduced-motion: no-preference)", () => {
    gsap.to("h1", { y: () => innerWidth < 1024 ? 0 : -0.25 * document.querySelector(".hero").offsetHeight, ease: "none",
      scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true, invalidateOnRefresh: true } });
  });
  ScrollTrigger.refresh();   // init can run after window load (late fonts); clamp() only resolves in a global refresh
  root.classList.remove("js");
  // animation clock stalled (static screenshot tools, background tabs): undo it all so nothing stays hidden
  const t0 = gsap.ticker.time;
  setTimeout(() => gsap.ticker.time - t0 < 1.5 && mm.revert(), 2500);
}));
