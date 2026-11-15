// SERVICE WORKER da Aptios: um "ajudante" que fica entre a página e a internet.
// - Páginas: tenta a internet primeiro; sem internet, usa a cópia guardada.
// - Arquivos fixos (ícones, Three.js, fontes): usa a cópia guardada e atualiza por trás.
// - API: nunca guarda (tokens, robôs e perguntas à IA precisam ser sempre de verdade),
//   menos o catálogo e os carros, que são iguais para todo mundo.
const VERSAO = 'aptios-v1';
const ESSENCIAL = ['/', '/ia', '/oficina', '/pista', '/static/icone-192.png'];
const PUBLICOS = ['/api/oficina/catalogo', '/api/pista/carro'];

self.addEventListener('install', (ev) => {
    ev.waitUntil(caches.open(VERSAO).then(c => c.addAll(ESSENCIAL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (ev) => {
    ev.waitUntil(caches.keys().then(nomes => Promise.all(nomes.filter(n => n !== VERSAO).map(n => caches.delete(n))))
        .then(() => self.clients.claim()));
});

async function internetPrimeiro(pedido) {
    const cache = await caches.open(VERSAO);
    try {
        const resposta = await fetch(pedido);
        if (resposta.ok) cache.put(pedido, resposta.clone());
        return resposta;
    } catch {
        return (await cache.match(pedido)) || (await cache.match('/')) || Response.error();
    }
}
async function guardadoPrimeiro(pedido) {
    const cache = await caches.open(VERSAO);
    const guardado = await cache.match(pedido);
    const daInternet = fetch(pedido).then(r => { if (r.ok || r.type === 'opaque') cache.put(pedido, r.clone()); return r; }).catch(() => guardado);
    return guardado || daInternet;
}

self.addEventListener('fetch', (ev) => {
    const pedido = ev.request, url = new URL(pedido.url);
    if (pedido.method !== 'GET') return;
    const local = url.origin === self.location.origin;
    if (local && url.pathname.startsWith('/api/')) {
        if (PUBLICOS.includes(url.pathname)) ev.respondWith(internetPrimeiro(pedido));
        return;
    }
    if (pedido.mode === 'navigate') { ev.respondWith(internetPrimeiro(pedido)); return; }
    if ((local && url.pathname.startsWith('/static/')) || url.hostname === 'cdn.jsdelivr.net' || url.hostname.endsWith('gstatic.com') || url.hostname === 'fonts.googleapis.com')
        ev.respondWith(guardadoPrimeiro(pedido));
});
