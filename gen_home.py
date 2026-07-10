import os
os.chdir("D:\\sign_language_game")

html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SignLingua - 手语学习平台</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#07050f;--surface:rgba(255,255,255,0.03);--surface-hover:rgba(255,255,255,0.06);--border:rgba(255,255,255,0.06);--text:#eeecf5;--text-dim:rgba(238,236,245,0.4);--text-mid:rgba(238,236,245,0.6);--primary:#7c3aed;--primary-light:#a78bfa;--primary-dim:rgba(124,58,237,0.15);--radius:14px}
html{scroll-behavior:smooth}
body{font-family:"Inter","Noto Sans SC",sans-serif;background:var(--bg);color:var(--text);overflow-x:hidden;min-height:100vh;font-size:13px;line-height:1.6}
#three-container{position:fixed;inset:0;z-index:1}
#three-container canvas{display:block;pointer-events:auto}
.orb{position:fixed;border-radius:50%;filter:blur(120px);pointer-events:none;z-index:0}
.orb-1{width:600px;height:600px;background:radial-gradient(circle,rgba(124,58,237,0.12),transparent);top:-200px;right:-150px;animation:da 25s ease-in-out infinite}
.orb-2{width:500px;height:500px;background:radial-gradient(circle,rgba(59,130,246,0.08),transparent);bottom:-150px;left:-100px;animation:db 30s ease-in-out infinite}
.orb-3{width:400px;height:400px;background:radial-gradient(circle,rgba(244,114,182,0.06),transparent);top:40%;left:30%;animation:dc 20s ease-in-out infinite}
@keyframes da{0%,100%{transform:translate(0,0)}50%{transform:translate(-120px,80px)}}
@keyframes db{0%,100%{transform:translate(0,0)}50%{transform:translate(100px,-120px)}}
@keyframes dc{0%,100%{transform:translate(-50%,-50%)}50%{transform:translate(-30%,-30%) scale(1.2)}}
.nav-wrap{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:100;width:calc(100% - 40px);max-width:1100px}
.nav{display:flex;align-items:center;justify-content:space-between;padding:10px 18px 10px 24px;background:rgba(7,5,15,0.65);backdrop-filter:blur(32px) saturate(1.4);-webkit-backdrop-filter:blur(32px) saturate(1.4);border:1px solid var(--border);border-radius:60px;box-shadow:0 8px 40px rgba(0,0,0,0.3)}
.nav-brand{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:700;letter-spacing:-0.2px}
.nav-brand .bi{width:30px;height:30px;background:linear-gradient(135deg,var(--primary),#a78bfa);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 2px 12px rgba(124,58,237,0.25)}
.nav-brand span{background:linear-gradient(135deg,var(--primary-light),#c4b5fd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.nav-brand em{-webkit-text-fill-color:rgba(255,255,255,0.2);font-style:normal;font-weight:400}
.nav-c{display:flex;gap:2px;align-items:center}
.nav-c a{display:flex;align-items:center;gap:5px;color:var(--text-mid);text-decoration:none;padding:7px 14px;border-radius:30px;font-size:12px;font-weight:500;transition:all 0.25s;white-space:nowrap}
.nav-c a:hover{color:var(--text);background:rgba(255,255,255,0.04)}
.nav-c a.active{color:#fff;background:var(--primary-dim)}
.nav-c a svg{width:14px;height:14px;opacity:0.6}
.nav-r{display:flex;align-items:center;gap:6px;position:relative}
.nav-r .ib{width:34px;height:34px;border:none;border-radius:50%;background:rgba(255,255,255,0.04);color:var(--text-mid);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.25s}
.nav-r .ib:hover{background:rgba(255,255,255,0.08);color:var(--text)}
.nav-r .ib svg{width:16px;height:16px}
.auth-dr{position:absolute;top:calc(100% + 8px);right:0;width:280px;background:rgba(10,8,20,0.92);backdrop-filter:blur(32px) saturate(1.4);border:1px solid var(--border);border-radius:16px;padding:20px;opacity:0;visibility:hidden;transform:translateY(-6px) scale(0.98);transition:all 0.3s cubic-bezier(0.22,1,0.36,1);box-shadow:0 24px 80px rgba(0,0,0,0.5);z-index:200}
.auth-dr.open{opacity:1;visibility:visible;transform:translateY(0) scale(1)}
.auth-dr .tabs{display:flex;gap:3px;background:rgba(255,255,255,0.03);border-radius:10px;padding:3px;margin-bottom:16px}
.auth-dr .tab{flex:1;padding:8px;border:none;border-radius:8px;background:transparent;color:var(--text-dim);font-size:12px;font-weight:600;cursor:pointer;transition:all 0.25s}
.auth-dr .tab.active{background:var(--primary-dim);color:var(--primary-light)}
.auth-dr .tab:hover:not(.active){color:var(--text-mid)}
.auth-dr .fg{margin-bottom:12px}
.auth-dr .fg label{display:block;font-size:11px;font-weight:500;color:var(--text-dim);margin-bottom:4px}
.auth-dr .fi{width:100%;padding:9px 12px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(255,255,255,0.03);color:#fff;font-size:13px;outline:none;transition:border-color 0.25s}
.auth-dr .fi:focus{border-color:rgba(124,58,237,0.3)}
.auth-dr .fi::placeholder{color:rgba(255,255,255,0.15)}
.auth-dr .as{width:100%;padding:10px;border:none;border-radius:8px;background:linear-gradient(135deg,var(--primary),#6d28d9);color:#fff;font-size:13px;font-weight:600;cursor:pointer;transition:all 0.25s;margin-top:4px}
.auth-dr .as:hover{opacity:0.9;transform:translateY(-1px)}
.auth-dr .ae{color:#f87171;font-size:12px;padding:6px 8px;background:rgba(248,113,113,0.06);border-radius:6px;margin-bottom:8px;display:none}
.auth-dr .ui{display:flex;align-items:center;gap:10px;padding:8px 0}
.auth-dr .ua{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,var(--primary),#f472b6);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700}
.auth-dr .ud{flex:1}
.auth-dr .ud .un{font-weight:600;font-size:13px}
.auth-dr .ud .um{font-size:11px;color:var(--text-dim)}
.auth-dr .lo{width:100%;padding:9px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:transparent;color:var(--text-dim);font-size:12px;cursor:pointer;transition:all 0.25s;margin-top:8px}
.auth-dr .lo:hover{background:rgba(239,68,68,0.08);color:#ef4444;border-color:rgba(239,68,68,0.15)}
.hero{position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:100px 24px 60px;text-align:center}
.hero-in{max-width:700px;animation:rise 0.9s cubic-bezier(0.22,1,0.36,1) both}
@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.hero-bd{display:inline-flex;align-items:center;gap:6px;padding:5px 14px;border-radius:20px;background:var(--primary-dim);border:1px solid rgba(124,58,237,0.15);font-size:11px;color:var(--primary-light);margin-bottom:22px;letter-spacing:0.3px}
.hero-bd .dot{width:5px;height:5px;border-radius:50%;background:#34d399;display:inline-block;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.hero h1{font-size:clamp(32px,5vw,58px);font-weight:900;line-height:1.12;margin-bottom:14px;letter-spacing:-0.02em}
.hero h1 .g{background:linear-gradient(135deg,#a78bfa,#7c3aed,#f472b6,#3b82f6);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shift 5s ease-in-out infinite}
@keyframes shift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.hero h1 .sl{display:block;font-size:0.5em;font-weight:500;color:var(--text-dim);margin-top:10px}
.hero p{font-size:13px;color:var(--text-dim);max-width:480px;margin:0 auto 26px}
.hero p strong{color:var(--text-mid);font-weight:500}
.hero-st{display:flex;justify-content:center;gap:8px;margin-bottom:28px;flex-wrap:wrap}
.sc{background:var(--surface);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:10px;padding:14px 24px;text-align:center;min-width:90px;transition:all 0.35s}
.sc:hover{transform:translateY(-2px);border-color:rgba(124,58,237,0.15);background:var(--surface-hover);box-shadow:0 8px 24px rgba(124,58,237,0.06)}
.sc .n{font-size:24px;font-weight:800;background:linear-gradient(135deg,var(--primary-light),#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block;line-height:1.2}
.sc .l{font-size:11px;color:var(--text-dim);margin-top:2px;display:block}
.hero-act{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.btn{padding:10px 22px;border:none;border-radius:30px;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn-p{background:linear-gradient(135deg,var(--primary),#6d28d9);color:#fff;box-shadow:0 3px 14px rgba(124,58,237,0.2)}
.btn-p:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(124,58,237,0.3)}
.btn-r{background:linear-gradient(135deg,#f472b6,#ec4899);color:#fff;box-shadow:0 3px 14px rgba(244,114,182,0.2)}
.btn-r:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(244,114,182,0.3)}
.btn-g{background:var(--surface);border:1px solid var(--border);color:var(--text)}
.btn-g:hover{background:var(--surface-hover);transform:translateY(-2px)}
.features-sec{position:relative;z-index:2;padding:50px 24px 70px;max-width:1000px;margin:0 auto}
.sec-lbl{text-align:center;font-size:10px;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--primary-light);opacity:0.5;margin-bottom:4px}
.sec-ttl{text-align:center;font-size:clamp(20px,2.5vw,30px);font-weight:800;margin-bottom:10px}
.sec-dsc{text-align:center;font-size:13px;color:var(--text-dim);max-width:450px;margin:0 auto 32px}
.fg{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.fc{background:var(--surface);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:var(--radius);padding:24px 20px;transition:all 0.35s;position:relative;overflow:hidden}
.fc::before{content:"";position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,transparent,var(--primary),transparent);opacity:0;transition:opacity 0.35s}
.fc:hover::before{opacity:1}
.fc:hover{transform:translateY(-3px);border-color:rgba(124,58,237,0.1);box-shadow:0 12px 32px rgba(124,58,237,0.04)}
.fc .fic{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:12px;background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(167,139,250,0.06));border:1px solid rgba(124,58,237,0.08)}
.fc .fic svg{width:20px;height:20px}
.fc h3{font-size:14px;font-weight:700;margin-bottom:6px}
.fc p{font-size:12px;color:var(--text-dim);line-height:1.6}
.footer{position:relative;z-index:2;text-align:center;padding:28px 24px;border-top:1px solid rgba(255,255,255,0.03);color:var(--text-dim);font-size:11px}
.footer strong{color:var(--primary-light)}
.scrl-h{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:4px;color:var(--text-dim);font-size:10px;opacity:0.35;animation:bob 2.5s infinite}
@keyframes bob{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(6px)}}
.scrl-h svg{width:14px;height:14px}
@media(max-width:768px){
.fg{grid-template-columns:1fr}.hero-st{gap:6px}.sc{min-width:70px;padding:10px 14px}.sc .n{font-size:18px}
.nav-wrap{width:calc(100% - 16px);top:10px}.nav{padding:8px 12px;border-radius:20px}.nav-c{gap:0}.nav-c a{padding:6px 10px;font-size:11px}.nav-c a span{display:none}
.hero{padding:80px 16px 40px}.hero h1{font-size:26px}.auth-dr{right:-10px;width:250px}
}
@media(max-width:480px){.nav-c a{padding:6px 8px}.nav-c a svg{width:16px;height:16px;opacity:0.8}}
</style>
</head>
<body>
<div id="three-container"></div>
<div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div>

<div class="nav-wrap">
<nav class="nav">
<div class="nav-brand"><div class="bi">&#x1f91f;</div><span>Sign<em>Lingua</em></span></div>
<div class="nav-c">
<a href="/" class="active"><svg data-lucide="home" width="14" height="14"></svg><span>&#x9996;&#x9875;</span></a>
<a href="/learn"><svg data-lucide="book-open" width="14" height="14"></svg><span>&#x5b66;&#x4e60;</span></a>
<a href="/camera-game"><svg data-lucide="camera" width="14" height="14"></svg><span>&#x6444;&#x50cf;&#x5934;</span></a>
<a href="/game"><svg data-lucide="gamepad-2" width="14" height="14"></svg><span>&#x6e38;&#x620f;</span></a>
<a href="/learning"><svg data-lucide="library" width="14" height="14"></svg><span>&#x8bcd;&#x5e93;</span></a>
<a href="/learn/review"><svg data-lucide="refresh-cw" width="14" height="14"></svg><span>&#x590d;&#x4e60;</span></a>
</div>
<div class="nav-r">
<button class="ib" id="authToggleBtn"><svg data-lucide="user" width="16" height="16"></svg></button>
<div class="auth-dr" id="authDrop">
<div id="authNotLoggedIn">
<div class="tabs">
<button class="tab active" data-tab="login">&#x767b;&#x5f55;</button>
<button class="tab" data-tab="register">&#x6ce8;&#x518c;</button>
</div>
<div class="ae" id="authError"></div>
<div class="fg"><label>&#x7528;&#x6237;&#x540d;</label><input type="text" id="authUsername" class="fi" placeholder="&#x7ed9;&#x81ea;&#x5df1;&#x8d77;&#x4e2a;&#x540d;&#x5b57;" maxlength="20"></div>
<div class="fg"><label>&#x5bc6;&#x7801;</label><input type="password" id="authPassword" class="fi" placeholder="&#x5bc6;&#x7801;"></div>
<div class="fg" id="confirmGroup" style="display:none"><label>&#x786e;&#x8ba4;&#x5bc6;&#x7801;</label><input type="password" id="authConfirm" class="fi" placeholder="&#x518d;&#x6b21;&#x8f93;&#x5165;&#x5bc6;&#x7801;"></div>
<button class="as" id="authSubmitBtn">&#x767b;&#x5f55;</button>
</div>
<div id="authLoggedIn" style="display:none">
<div class="ui"><div class="ua" id="userAvatar">&#x1f91f;</div><div class="ud"><div class="un" id="userName">&#x7528;&#x6237;</div><div class="um" id="userMeta">Lv.1 &middot; 0 XP</div></div></div>
<button class="lo" id="logoutBtn">&#x9000;&#x51fa;&#x767b;&#x5f55;</button>
</div>
</div>
</div>
</nav>
</div>

<section class="hero">
<div class="hero-in">
<div class="hero-bd"><span class="dot"></span>&#x57fa;&#x4e8e; 1098 &#x4e2a;&#x771f;&#x5b9e;&#x624b;&#x8bed;&#x89c6;&#x9891;</div>
<h1>&#x7528; <span class="g">&#x624b;&#x8bed;</span><span class="sl">&#x67b6;&#x8d77;&#x6c9f;&#x901a;&#x7684;&#x6881;</span></h1>
<p><strong>AI &#x9a71;&#x52a8;</strong> &middot; 12 &#x9636;&#x6bb5;&#x7cfb;&#x7edf;&#x8bfe;&#x7a0b; &middot; &#x5b9e;&#x65f6;&#x6444;&#x50cf;&#x5934;&#x8bc6;&#x522b; &middot; &#x8ba9;&#x6bcf;&#x4e2a;&#x4eba;&#x90fd;&#x80fd;&#x4e0e;&#x542c;&#x969c;&#x4eba;&#x58eb;&#x81ea;&#x7531;&#x4ea4;&#x6d41;</p>
<div class="hero-st">
<div class="sc"><span class="n" id="statTotal">0</span><span class="l">&#x8bcd;&#x6c47;&#x91cf;</span></div>
<div class="sc"><span class="n" id="statBasic">0</span><span class="l">&#x57fa;&#x7840;</span></div>
<div class="sc"><span class="n" id="statCommon">0</span><span class="l">&#x8fdb;&#x9636;</span></div>
<div class="sc"><span class="n" id="statTypes">0</span><span class="l">&#x5206;&#x7c7b;</span></div>
</div>
<div class="hero-act">
<a href="/learn" class="btn btn-p">&#x5f00;&#x59cb;&#x5b66;&#x4e60;</a>
<a href="/camera-game" class="btn btn-r">&#x6444;&#x50cf;&#x5934;&#x6311;&#x6218;</a>
<a href="/game" class="btn btn-g">&#x95ef;&#x5173;&#x6e38;&#x620f;</a>
</div>
</div>
<div class="scrl-h"><svg data-lucide="chevron-down" width="14" height="14"></svg><span>&#x63a2;&#x7d22;</span></div>
</section>

<section class="features-sec">
<div class="sec-lbl">Features</div>
<h2 class="sec-ttl">&#x5168;&#x65b9;&#x4f4d;&#x5b66;&#x4e60;&#x4f53;&#x9a8c;</h2>
<p class="sec-dsc">&#x4ece;&#x89c6;&#x9891;&#x5b66;&#x4e60;&#x5230;&#x6444;&#x50cf;&#x5934;&#x5b9e;&#x65f6;&#x8bc6;&#x522b;&#xff0c;AI &#x9a71;&#x52a8;&#x7684;&#x624b;&#x8bed;&#x5b66;&#x4e60;&#x65b0;&#x65b9;&#x5f0f;</p>
<div class="fg">
<div class="fc"><div class="fic"><svg data-lucide="map" width="20" height="20"></svg></div><h3>12 &#x9636;&#x6bb5;&#x95ef;&#x5173;</h3><p>&#x4ece;&#x79f0;&#x547c;&#x5230;&#x804b;&#x4eba;&#x6587;&#x5316;&#xff0c;&#x7cfb;&#x7edf;&#x5316;&#x5b66;&#x4e60;&#x5730;&#x56fe;&#xff0c;&#x6bcf;&#x9636;&#x6bb5;&#x83b7;&#x5f97;&#x661f;&#x7ea7;&#x8bc4;&#x4ef7;</p></div>
<div class="fc"><div class="fic"><svg data-lucide="scan" width="20" height="20"></svg></div><h3>&#x6444;&#x50cf;&#x5934;&#x8bc6;&#x522b;</h3><p>MediaPipe &#x5b9e;&#x65f6;&#x624b;&#x90e8;&#x8ffd;&#x8e2a;&#xff0c;AI &#x8bc4;&#x5206;&#x5f15;&#x64ce;&#x5206;&#x6790;&#x4f60;&#x7684;&#x624b;&#x52bf;&#x51c6;&#x786e;&#x5ea6;</p></div>
<div class="fc"><div class="fic"><svg data-lucide="brain" width="20" height="20"></svg></div><h3>&#x667a;&#x80fd;&#x590d;&#x4e60;</h3><p>&#x57fa;&#x4e8e;&#x95f4;&#x9694;&#x91cd;&#x590d;&#x7b97;&#x6cd5;&#xff0c;&#x8584;&#x5f31;&#x8bcd;&#x4f18;&#x5148;&#x590d;&#x4e60;&#xff0c;&#x5de9;&#x56fa;&#x957f;&#x671f;&#x8bb0;&#x5fc6;</p></div>
<div class="fc"><div class="fic"><svg data-lucide="target" width="20" height="20"></svg></div><h3>&#x95ef;&#x5173;&#x6e38;&#x620f;</h3><p>&#x56db;&#x9009;&#x4e00;&#x5feb;&#x901f;&#x7b54;&#x9898;&#xff0c;&#x8ba1;&#x65f6;&#x6311;&#x6218;&#xff0c;&#x79ef;&#x5206;&#x6392;&#x884c;&#x699c;&#x4e0e;&#x670b;&#x53cb;&#x7ade;&#x6280;</p></div>
<div class="fc"><div class="fic"><svg data-lucide="book-open" width="20" height="20"></svg></div><h3>1098 &#x8bcd;&#x8bcd;&#x5e93;</h3><p>25 &#x4e2a;&#x8bed;&#x4e49;&#x5206;&#x7c7b;&#xff0c;10 &#x79cd;&#x8bcd;&#x6027;&#x6807;&#x6ce8;&#xff0c;DeepSeek AI &#x7cbe;&#x51c6;&#x5206;&#x7c7b;</p></div>
<div class="fc"><div class="fic"><svg data-lucide="hand" width="20" height="20"></svg></div><h3>&#x804b;&#x6587;&#x5316;&#x878d;&#x5408;</h3><p>&#x5305;&#x542b;&#x624b;&#x8bed;&#x8bd7;&#x3001;&#x624b;&#x8bed;&#x6b4c;&#x3001;&#x804b;&#x4eba;&#x6587;&#x5316;&#x7b49;&#x7279;&#x8272;&#x5185;&#x5bb9;&#xff0c;&#x4e0d;&#x53ea;&#x662f;&#x8bcd;&#x6c47;</p></div>
</div>
</section>

<footer class="footer">SignLingua &middot; &#x7528;&#x6280;&#x672f;&#x8fde;&#x63a5;&#x65e0;&#x58f0;&#x4e16;&#x754c; &middot; <strong>1098</strong> &#x4e2a;&#x624b;&#x8bed;&#x8bcd;&#x6c47; &middot; <strong>12</strong> &#x9636;&#x6bb5;&#x8bfe;&#x7a0b;</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="/static/js/three-scene.js"></script>
<script src="/static/js/auth.js"></script>
<script>
lucide.createIcons();
var BASE="",authOpen=false,authTab="login";
document.querySelectorAll(".tab").forEach(function(t){
t.addEventListener("click",function(){
document.querySelectorAll(".tab").forEach(function(x){x.classList.remove("active")});
t.classList.add("active");authTab=t.dataset.tab;
var r=authTab==="register";
document.getElementById("authSubmitBtn").textContent=r?"&#x6ce8;&#x518c;":"&#x767b;&#x5f55;";
document.getElementById("confirmGroup").style.display=r?"block":"none";
document.getElementById("authError").style.display="none";
});
});
document.getElementById("authToggleBtn").addEventListener("click",function(e){
e.stopPropagation();authOpen=!authOpen;
document.getElementById("authDrop").classList.toggle("open",authOpen);
});
document.addEventListener("click",function(e){
var d=document.getElementById("authDrop");
if(authOpen&&!d.contains(e.target)&&e.target!==document.getElementById("authToggleBtn")){authOpen=false;d.classList.remove("open");}
});
document.getElementById("authSubmitBtn").addEventListener("click",async function(){
var u=document.getElementById("authUsername").value.trim();
var p=document.getElementById("authPassword").value,e=document.getElementById("authError"),r;
if(authTab==="register"){var c=document.getElementById("authConfirm").value;if(p!==c){e.textContent="&#x4e24;&#x6b21;&#x5bc6;&#x7801;&#x4e0d;&#x4e00;&#x81f4;";e.style.display="block";return}r=await Auth.register(u,p,c);}
else{r=await Auth.login(u,p);}
if(r.error){e.textContent=r.error;e.style.display="block";return}
authOpen=false;document.getElementById("authDrop").classList.remove("open");
document.getElementById("authNotLoggedIn").style.display="none";
document.getElementById("authLoggedIn").style.display="block";
document.getElementById("userName").textContent=r.user.username;
document.getElementById("userMeta").textContent="Lv."+(r.user.level||1)+" &#183; "+(r.user.xp||0)+" XP";
if(typeof lucide!=="undefined")lucide.createIcons();
});
document.getElementById("logoutBtn").addEventListener("click",async function(){await Auth.logout();document.getElementById("authLoggedIn").style.display="none";document.getElementById("authNotLoggedIn").style.display="block";});
Auth.ready().then(function(){
if(Auth.isLoggedIn()){var u=Auth.getUser();
document.getElementById("authNotLoggedIn").style.display="none";
document.getElementById("authLoggedIn").style.display="block";
document.getElementById("userName").textContent=u.username;
document.getElementById("userMeta").textContent="Lv."+(u.level||1)+" &#183; "+(u.xp||0)+" XP";
}
});
async function loadStats(){
try{
var r=await fetch(BASE+"/api/sign/stats");var d=await r.json();
if(d.code===0){var s=d.data;
document.getElementById("statTotal").textContent=s.total;
var b=s.datasets.find(function(x){return x.dataset==="basic";});
document.getElementById("statBasic").textContent=b?b.cnt:0;
var c=s.datasets.find(function(x){return x.dataset==="common";});
document.getElementById("statCommon").textContent=c?c.cnt:0;
document.getElementById("statTypes").textContent=s.categories.length;
}
}catch(e){}
}
loadStats();
</script>
</body>
</html>"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Written:", len(html), "bytes")
