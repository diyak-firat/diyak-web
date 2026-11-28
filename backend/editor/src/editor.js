/*
 * Panel duyuru editörü (K-26). Araç çubuğu PANEL.md §9'daki izin listesiyle sınırlıdır:
 * kalın, italik, başlık (h2/h3), madde ve numaralı liste, alıntı, bağlantı.
 * Sunucu, gelen HTML'i her kayıtta nh3 ile yeniden temizler; buradaki kısıtlar yalnızca kolaylıktır.
 *
 * JavaScript kapalıysa sayfadaki <textarea name="govde"> olduğu gibi kullanılır.
 * Derlemek için: cd backend/editor && npm ci && npm run build
 */
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';

const IZINLI_ADRES = /^(https:\/\/|mailto:)/i;

const DUGMELER = [
  { ad: 'Kalın', komut: (e) => e.chain().focus().toggleBold().run(), aktif: (e) => e.isActive('bold') },
  { ad: 'İtalik', komut: (e) => e.chain().focus().toggleItalic().run(), aktif: (e) => e.isActive('italic') },
  { ayrac: true },
  {
    ad: 'Başlık',
    komut: (e) => e.chain().focus().toggleHeading({ level: 2 }).run(),
    aktif: (e) => e.isActive('heading', { level: 2 }),
  },
  {
    ad: 'Alt başlık',
    komut: (e) => e.chain().focus().toggleHeading({ level: 3 }).run(),
    aktif: (e) => e.isActive('heading', { level: 3 }),
  },
  { ayrac: true },
  { ad: 'Madde listesi', komut: (e) => e.chain().focus().toggleBulletList().run(), aktif: (e) => e.isActive('bulletList') },
  { ad: 'Numaralı liste', komut: (e) => e.chain().focus().toggleOrderedList().run(), aktif: (e) => e.isActive('orderedList') },
  {
    ad: 'İçeri al',
    ipucu: 'Liste maddesini bir üsttekinin altına alır (Tab)',
    komut: (e) => e.chain().focus().sinkListItem('listItem').run(),
    etkin: (e) => e.can().sinkListItem('listItem'),
  },
  {
    ad: 'Dışarı al',
    ipucu: 'Alt maddeyi bir üst düzeye çıkarır (Shift+Tab)',
    komut: (e) => e.chain().focus().liftListItem('listItem').run(),
    etkin: (e) => e.isActive('listItem') && e.can().liftListItem('listItem'),
  },
  { ad: 'Alıntı', komut: (e) => e.chain().focus().toggleBlockquote().run(), aktif: (e) => e.isActive('blockquote') },
  { ayrac: true },
  { ad: 'Bağlantı', baglanti: true, aktif: (e) => e.isActive('link') },
  { ayrac: true },
  { ad: 'Geri al', komut: (e) => e.chain().focus().undo().run(), etkin: (e) => e.can().undo() },
  { ad: 'Yinele', komut: (e) => e.chain().focus().redo().run(), etkin: (e) => e.can().redo() },
];

function oge(etiket, nitelikler = {}, metin = '') {
  const el = document.createElement(etiket);
  for (const [k, v] of Object.entries(nitelikler)) el.setAttribute(k, v);
  if (metin) el.textContent = metin;
  return el;
}

function kur(kutu) {
  const alan = kutu.querySelector('textarea');
  const etiketId = kutu.dataset.etiket;
  if (!alan) return;

  const cubuk = oge('div', { class: 'editor-cubuk', role: 'toolbar', 'aria-label': 'Metin biçimi' });
  const baglantiFormu = oge('div', { class: 'editor-baglanti', hidden: '' });
  const metinGirdisi = oge('input', { type: 'text', 'aria-label': 'Görünecek metin', placeholder: 'Görünecek metin' });
  const adresGirdisi = oge('input', {
    type: 'url',
    placeholder: 'https://… veya mailto:…',
    'aria-label': 'Bağlantı adresi',
  });
  const baglantiEkle = oge('button', { type: 'button' }, 'Bağlantıyı ekle');
  const baglantiKaldir = oge('button', { type: 'button', class: 'dugme-ikincil' }, 'Bağlantıyı kaldır');
  const baglantiVazgec = oge('button', { type: 'button', class: 'metin-dugme' }, 'Vazgeç');
  const baglantiHata = oge('p', { class: 'form-hata', role: 'alert', hidden: '' });
  baglantiFormu.append(metinGirdisi, adresGirdisi, baglantiEkle, baglantiKaldir, baglantiVazgec, baglantiHata);

  const yuzey = oge('div', { class: 'editor-yuzey' });
  alan.hidden = true;
  alan.after(cubuk, baglantiFormu, yuzey);

  const editor = new Editor({
    element: yuzey,
    content: alan.value,
    extensions: [
      StarterKit.configure({
        heading: { levels: [2, 3] },
        code: false,
        codeBlock: false,
        horizontalRule: false,
        strike: false,
        underline: false,
        link: {
          openOnClick: false,
          autolink: true,
          protocols: ['https', 'mailto'],
          defaultProtocol: 'https',
          isAllowedUri: (adres) => IZINLI_ADRES.test(adres),
          HTMLAttributes: { rel: 'noopener noreferrer', target: null },
        },
      }),
    ],
    editorProps: {
      attributes: {
        role: 'textbox',
        'aria-multiline': 'true',
        ...(etiketId ? { 'aria-labelledby': etiketId } : {}),
      },
    },
  });

  const dugmeler = [];
  for (const tanim of DUGMELER) {
    if (tanim.ayrac) {
      cubuk.append(oge('span', { class: 'editor-ayrac', 'aria-hidden': 'true' }));
      continue;
    }
    const d = oge('button', { type: 'button', 'aria-pressed': 'false' }, tanim.ad);
    if (tanim.ipucu) d.title = tanim.ipucu;
    if (!tanim.aktif) d.removeAttribute('aria-pressed');
    d.addEventListener('click', () => (tanim.baglanti ? baglantiAc() : tanim.komut(editor)));
    cubuk.append(d);
    dugmeler.push([d, tanim]);
  }

  function seciliMetin() {
    const { from, to } = editor.state.selection;
    return editor.state.doc.textBetween(from, to, ' ');
  }
  function baglantiAc() {
    // İmleç bir bağlantının içindeyse bağlantının tamamı seçilir; böylece düzenlenebilir veya kaldırılabilir.
    if (editor.isActive('link')) editor.chain().extendMarkRange('link').run();
    metinGirdisi.value = seciliMetin();
    adresGirdisi.value = editor.getAttributes('link').href || '';
    baglantiHata.hidden = true;
    baglantiKaldir.hidden = !editor.isActive('link');
    baglantiFormu.hidden = false;
    (metinGirdisi.value ? adresGirdisi : metinGirdisi).focus();
  }
  function baglantiKapat() {
    baglantiFormu.hidden = true;
    editor.commands.focus();
  }
  function baglantiUygula() {
    const adres = adresGirdisi.value.trim();
    if (!IZINLI_ADRES.test(adres)) {
      baglantiHata.textContent = 'Adres https:// veya mailto: ile başlamalı.';
      baglantiHata.hidden = false;
      adresGirdisi.focus();
      return;
    }
    const yazilan = metinGirdisi.value;
    if (yazilan.trim() && yazilan === seciliMetin()) {
      // Seçili metin aynen kalıyor: yalnızca bağlantı eklenir (biçimi korunur).
      editor.chain().focus().extendMarkRange('link').setLink({ href: adres }).run();
    } else {
      // Seçim yoksa veya metin değiştiyse, metin bağlantılı olarak yerine yazılır.
      // Seçimin başındaki ve sonundaki boşluklar bağlantının dışında korunur.
      const secili = seciliMetin();
      const bas = secili.match(/^\s*/)[0];
      const son = secili.trim() ? secili.match(/\s*$/)[0] : '';
      const metin = yazilan.trim() || adres.replace(/^mailto:/i, '');
      const parcalar = [{ type: 'text', text: metin, marks: [{ type: 'link', attrs: { href: adres } }] }];
      if (bas) parcalar.unshift({ type: 'text', text: bas });
      if (son) parcalar.push({ type: 'text', text: son });
      editor.chain().focus().insertContent(parcalar).unsetMark('link').run();
    }
    baglantiKapat();
  }
  baglantiEkle.addEventListener('click', baglantiUygula);
  const enterEscape = (olay) => {
    if (olay.key === 'Enter') {
      olay.preventDefault();
      baglantiUygula();
    } else if (olay.key === 'Escape') {
      baglantiKapat();
    }
  };
  metinGirdisi.addEventListener('keydown', enterEscape);
  adresGirdisi.addEventListener('keydown', enterEscape);
  baglantiKaldir.addEventListener('click', () => {
    editor.chain().focus().extendMarkRange('link').unsetLink().run();
    baglantiKapat();
  });
  baglantiVazgec.addEventListener('click', baglantiKapat);

  function guncelle() {
    for (const [d, tanim] of dugmeler) {
      if (tanim.aktif) d.setAttribute('aria-pressed', String(tanim.aktif(editor)));
      if (tanim.etkin) d.disabled = !tanim.etkin(editor);
    }
  }
  function esitle() {
    alan.value = editor.isEmpty ? '' : editor.getHTML();
    kutu.dispatchEvent(new CustomEvent('editor-degisti', { bubbles: true, detail: { html: alan.value } }));
  }
  editor.on('selectionUpdate', guncelle);
  editor.on('transaction', guncelle);
  editor.on('update', esitle);
  alan.form?.addEventListener('submit', esitle);
  guncelle();
}

document.querySelectorAll('[data-editor]').forEach(kur);
