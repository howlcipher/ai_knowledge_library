/**
 * AI_LIB Frontend Application Controller
 * Shared by the landing page and every Jekyll-rendered doc page.
 * Handles theme switching, the mobile nav drawer, and (landing page
 * only) localization and colorblind mode. Every control is optional —
 * doc pages only render the theme toggle and hamburger menu, while the
 * landing page also renders the language select and colorblind toggle.
 */

class MechaApp {
    constructor() {
        this.root = document.documentElement;
        this.themeToggle = document.getElementById('themeToggle');
        this.langSelect = document.getElementById('langSelect');
        this.colorblindToggle = document.getElementById('colorblindToggle');
        this.hamburger = document.getElementById('hamburger-menu');
        this.navLinks = document.getElementById('nav-links');

        this.i18nData = this.getTranslations();

        this.init();
    }

    /**
     * Initializes the application state based on user preferences.
     */
    init() {
        this.bindEvents();
        this.detectInitialTheme();
        if (this.langSelect) {
            this.detectInitialLanguage();
        }
    }

    /**
     * Binds event listeners to whichever UI controls are present on
     * the current page.
     */
    bindEvents() {
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        if (this.colorblindToggle) {
            this.colorblindToggle.addEventListener('click', () => this.toggleColorblindMode());
        }
        if (this.langSelect) {
            this.langSelect.addEventListener('change', (e) => this.translatePage(e.target.value));
        }
        if (this.hamburger && this.navLinks) {
            this.hamburger.addEventListener('click', (e) => {
                e.stopPropagation();
                this.navLinks.classList.toggle('active');
                this.hamburger.classList.toggle('open');
            });
            document.addEventListener('click', (event) => {
                if (!this.navLinks.contains(event.target) && this.navLinks.classList.contains('active')) {
                    this.navLinks.classList.remove('active');
                    this.hamburger.classList.remove('open');
                }
            });
        }
    }

    /**
     * Detects system color scheme preference and applies the corresponding theme.
     */
    detectInitialTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            this.setTheme('light');
        } else {
            this.setTheme('dark');
        }
    }

    /**
     * Detects browser language and translates the page if supported.
     */
    detectInitialLanguage() {
        const userLang = navigator.language.substring(0, 2);
        if (this.i18nData[userLang]) {
            this.langSelect.value = userLang;
            this.translatePage(userLang);
        } else {
            this.translatePage('en');
        }
    }

    /**
     * Sets the application theme.
     * @param {string} theme - "light", "matrix", or "dark".
     */
    setTheme(theme) {
        if (theme === 'light') {
            this.root.setAttribute('data-theme', 'light');
            if (this.themeToggle) this.themeToggle.textContent = 'DAY';
        } else if (theme === 'matrix') {
            this.root.setAttribute('data-theme', 'matrix');
            if (this.themeToggle) this.themeToggle.textContent = 'NEURO';
        } else {
            this.root.setAttribute('data-theme', 'dark');
            if (this.themeToggle) this.themeToggle.textContent = 'NIGHT';
        }
    }

    /**
     * Cycles dark -> light -> matrix -> dark.
     */
    toggleTheme() {
        const currentTheme = this.root.getAttribute('data-theme');
        if (currentTheme === 'light') {
            this.setTheme('matrix');
        } else if (currentTheme === 'matrix') {
            this.setTheme('dark');
        } else {
            this.setTheme('light');
        }
    }

    /**
     * Toggles colorblind accessibility mode.
     */
    toggleColorblindMode() {
        const isColorblind = this.root.getAttribute('data-colorblind') === 'true';
        if (isColorblind) {
            this.root.setAttribute('data-colorblind', 'false');
            this.colorblindToggle.classList.remove('active');
        } else {
            this.root.setAttribute('data-colorblind', 'true');
            this.colorblindToggle.classList.add('active');
        }
    }

    /**
     * Translates all elements with data-i18n attribute based on the selected language.
     * @param {string} lang - The language code (e.g., 'en', 'ja', 'es').
     */
    translatePage(lang) {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (this.i18nData[lang] && this.i18nData[lang][key]) {
                el.textContent = this.i18nData[lang][key];
            }
        });
    }

    /**
     * Returns the localized dictionary mapping for all supported languages.
     * Landing-page copy only — doc pages are raw markdown/HTML with no
     * data-i18n spans.
     * @returns {Object} Localization dictionary
     */
    getTranslations() {
        return {
            en: {
                nav_features: "[FEATURES]", nav_docs: "[API_DOCS]", colorblind_mode: "COLORBLIND_MODE",
                hero_title: "SUPERCHARGE YOUR AI CONTEXT",
                hero_subtitle: "> A HIGHLY STRUCTURED, LOCALLY HOSTED KNOWLEDGE GRAPH AND VECTOR DATABASE BUILT FOR ADVANCED AUTONOMOUS AGENTS. COMPLETE WITH PGVECTOR INTEGRATION AND NATIVE GO INSTALLERS.",
                hero_btn_download: "EXECUTE INSTALL", hero_btn_docs: "READ MANUAL",
                feat_1_title: "ADVANCED RAG", feat_1_desc: "> Seamless PgVector and ChromaDB integration for deep semantic search and context retrieval.",
                feat_2_title: "GO CLI INSTALLER", feat_2_desc: "> Lightning-fast native Cobra CLI installer to seamlessly manage dependencies and global links.",
                feat_3_title: "AUTOMATED WEBHOOKS", feat_3_desc: "> Background FastAPI servers that automatically sync and embed incoming repository changes.",
                download_title: "SYSTEM DOWNLOADS", download_subtitle: "> Select your target operating system to download the latest compiled executable:",
                btn_copy: "COPY", btn_copied: "COPIED", footer_text: "> Built for the open-source agentic community. Open sourced on ",
                download_repo_link: "> SOURCE CODE REPOSITORY: "
            },
            ja: {
                nav_features: "[機能]", nav_docs: "[API_仕様]", colorblind_mode: "色覚サポート",
                hero_title: "AIコンテキストを起動せよ",
                hero_subtitle: "> 高度な自律型エージェントのために構築された、ローカルホストのナレッジグラフおよびベクトルデータベース。PGVECTOR統合とGOインストーラーを完全装備。",
                hero_btn_download: "インストール実行", hero_btn_docs: "マニュアル参照",
                feat_1_title: "高度なRAG", feat_1_desc: "> PgVectorとChromaDBのシームレスな統合による、深層意味検索とコンテキスト抽出。",
                feat_2_title: "GO CLI インストーラー", feat_2_desc: "> 依存関係を管理する超高速ネイティブCobra CLIインストーラー。",
                feat_3_title: "自動化WEBHOOK", feat_3_desc: "> バックグラウンドのFastAPIサーバーが、リポジトリの変更を自動同期。",
                download_title: "システムダウンロード", download_subtitle: "> ターゲットOSを選択して、最新のコンパイル済み実行可能ファイルをダウンロードします：",
                btn_copy: "コピー", btn_copied: "コピー完了", footer_text: "> オープンソースのエージェントコミュニティへ。提供元：",
                download_repo_link: "> ソースコードリポジトリ: "
            },
            es: {
                nav_features: "[CARACTERÍSTICAS]", nav_docs: "[DOCS_API]", colorblind_mode: "MODO_DALTÓNICO",
                hero_title: "SOBRECARGA TU CONTEXTO IA",
                hero_subtitle: "> UN GRAFO DE CONOCIMIENTO Y BASE DE DATOS VECTORIAL ALOJADA LOCALMENTE PARA AGENTES AUTÓNOMOS AVANZADOS. INTEGRACIÓN PGVECTOR E INSTALADORES GO.",
                hero_btn_download: "EJECUTAR INSTALACIÓN", hero_btn_docs: "LEER MANUAL",
                feat_1_title: "RAG AVANZADO", feat_1_desc: "> Integración de PgVector y ChromaDB para búsqueda semántica profunda.",
                feat_2_title: "INSTALADOR GO CLI", feat_2_desc: "> Instalador nativo ultrarrápido para gestionar dependencias.",
                feat_3_title: "WEBHOOKS AUTOMATIZADOS", feat_3_desc: "> Servidores FastAPI en segundo plano para sincronizar cambios.",
                download_title: "DESCARGAS DEL SISTEMA", download_subtitle: "> Selecciona tu sistema operativo objetivo para descargar el último ejecutable compilado:",
                btn_copy: "COPIAR", btn_copied: "COPIADO", footer_text: "> Construido para la comunidad de código abierto. Código fuente en ",
                download_repo_link: "> REPOSITORIO DE CÓDIGO FUENTE: "
            },
            zh: {
                nav_features: "[功能]", nav_docs: "[API文档]", colorblind_mode: "色盲模式",
                hero_title: "增强AI上下文",
                hero_subtitle: "> 专为高级自主代理构建的本地托管知识图谱和向量数据库。集成PGVECTOR和原生GO安装程序。",
                hero_btn_download: "执行安装", hero_btn_docs: "阅读手册",
                feat_1_title: "高级RAG", feat_1_desc: "> 无缝集成PgVector和ChromaDB，用于深度语义搜索。",
                feat_2_title: "GO CLI 安装程序", feat_2_desc: "> 极速原生CLI安装程序，无缝管理依赖项。",
                feat_3_title: "自动WEBHOOK", feat_3_desc: "> 后台FastAPI服务器自动同步存储库更改。",
                download_title: "系统下载", download_subtitle: "> 选择您的目标操作系统以直接下载最新编译的可执行文件：",
                btn_copy: "复制", btn_copied: "已复制", footer_text: "> 为开源代理社区构建。开源于 ",
                download_repo_link: "> 源代码存储库： "
            },
            fr: {
                nav_features: "[FONCTIONNALITÉS]", nav_docs: "[DOCS_API]", colorblind_mode: "MODE_DALTONIEN",
                hero_title: "SURCHARGEZ VOTRE CONTEXTE IA",
                hero_subtitle: "> UN GRAPHE DE CONNAISSANCES ET UNE BASE VECTORIELLE HÉBERGÉS LOCALEMENT POUR LES AGENTS AUTONOMES AVANCÉS. INTÉGRATION PGVECTOR ET INSTALLATEURS GO.",
                hero_btn_download: "EXÉCUTER INSTALLATION", hero_btn_docs: "LIRE MANUEL",
                feat_1_title: "RAG AVANCÉ", feat_1_desc: "> Intégration PgVector et ChromaDB pour la recherche sémantique profonde.",
                feat_2_title: "INSTALLATEUR GO CLI", feat_2_desc: "> Installateur natif ultra-rapide pour gérer les dépendances.",
                feat_3_title: "WEBHOOKS AUTOMATISÉS", feat_3_desc: "> Serveurs FastAPI en arrière-plan pour synchroniser les changements.",
                download_title: "TÉLÉCHARGEMENTS DU SYSTÈME", download_subtitle: "> Sélectionnez votre système d'exploitation cible pour télécharger le dernier exécutable compilé :",
                btn_copy: "COPIER", btn_copied: "COPIÉ", footer_text: "> Construit pour la communauté open source. Code source sur ",
                download_repo_link: "> DÉPÔT DE CODE SOURCE : "
            },
            de: {
                nav_features: "[FUNKTIONEN]", nav_docs: "[API_DOKU]", colorblind_mode: "FARBBLIND_MODUS",
                hero_title: "SUPERCHARGE DEINEN KI-KONTEXT",
                hero_subtitle: "> EIN HOCHSTRUKTURIERTER, LOKAL GEHOSTETER WISSENSGRAPH UND EINE VEKTORDATENBANK FÜR AUTONOME AGENTEN. MIT PGVECTOR-INTEGRATION UND GO-INSTALLERN.",
                hero_btn_download: "INSTALLATION AUSFÜHREN", hero_btn_docs: "HANDBUCH LESEN",
                feat_1_title: "FORTSCHRITTLICHES RAG", feat_1_desc: "> Nahtlose PgVector- und ChromaDB-Integration für tiefe semantische Suche.",
                feat_2_title: "GO CLI INSTALLER", feat_2_desc: "> Blitzschneller nativer CLI-Installer zur Verwaltung von Abhängigkeiten.",
                feat_3_title: "AUTOMATISIERTE WEBHOOKS", feat_3_desc: "> Hintergrund-FastAPI-Server zur automatischen Synchronisierung.",
                download_title: "SYSTEM-DOWNLOADS", download_subtitle: "> Wählen Sie Ihr Zielbetriebssystem aus, um die neueste kompilierte ausführbare Datei herunterzuladen:",
                btn_copy: "KOPIEREN", btn_copied: "KOPIERT", footer_text: "> Gebaut für die Open-Source-Community. Quellcode auf ",
                download_repo_link: "> QUELLCODE-REPOSITORY: "
            }
        };
    }
}

// Initialize application on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MechaApp();
});
