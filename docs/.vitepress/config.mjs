import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'GWorkspace Toolbox',
  description: 'Tools for Google Workspace administrators',
  base: '/GWorkspace-toolbox/',

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Home', link: '/' },
          { text: 'Installation', link: '/installation' },
          { text: 'Features', link: '/features' },
          { text: 'FAQ', link: '/faq' }
        ],
        sidebar: [
          {
            text: 'Getting Started',
            items: [
              { text: 'Introduction', link: '/' },
              { text: 'Installation', link: '/installation' },
              { text: 'Quick Start', link: '/quickstart' }
            ]
          },
          {
            text: 'Features',
            items: [
              { text: 'Overview', link: '/features' },
              { text: 'Alias Extractor', link: '/features/alias-extractor' },
              { text: 'Attribute Injector', link: '/features/attribute-injector' },
              { text: 'OU Group Sync', link: '/features/ou-group-sync' }
            ]
          },
          {
            text: 'Help',
            items: [
              { text: 'FAQ', link: '/faq' },
              { text: 'Troubleshooting', link: '/troubleshooting' }
            ]
          }
        ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 GWorkspace Toolbox Contributors'
        }
      }
    },
    es: {
      label: 'Español',
      lang: 'es',
      link: '/es/',
      themeConfig: {
        nav: [
          { text: 'Inicio', link: '/es/' },
          { text: 'Instalación', link: '/es/installation' },
          { text: 'Características', link: '/es/features' },
          { text: 'FAQ', link: '/es/faq' }
        ],
        sidebar: [
          {
            text: 'Comenzar',
            items: [
              { text: 'Introducción', link: '/es/' },
              { text: 'Instalación', link: '/es/installation' },
              { text: 'Inicio Rápido', link: '/es/quickstart' }
            ]
          },
          {
            text: 'Características',
            items: [
              { text: 'Resumen', link: '/es/features' },
              { text: 'Extractor de Alias', link: '/es/features/alias-extractor' },
              { text: 'Inyector de Atributos', link: '/es/features/attribute-injector' },
              { text: 'Sincronización de Grupos OU', link: '/es/features/ou-group-sync' }
            ]
          },
          {
            text: 'Ayuda',
            items: [
              { text: 'FAQ', link: '/es/faq' },
              { text: 'Solución de Problemas', link: '/es/troubleshooting' }
            ]
          }
        ],
        footer: {
          message: 'Publicado bajo la Licencia MIT.',
          copyright: 'Copyright © 2024 Colaboradores de GWorkspace Toolbox'
        }
      }
    },
    pt: {
      label: 'Português',
      lang: 'pt',
      link: '/pt/',
      themeConfig: {
        nav: [
          { text: 'Início', link: '/pt/' },
          { text: 'Instalação', link: '/pt/installation' },
          { text: 'Recursos', link: '/pt/features' },
          { text: 'FAQ', link: '/pt/faq' }
        ],
        sidebar: [
          {
            text: 'Primeiros Passos',
            items: [
              { text: 'Introdução', link: '/pt/' },
              { text: 'Instalação', link: '/pt/installation' },
              { text: 'Início Rápido', link: '/pt/quickstart' }
            ]
          },
          {
            text: 'Recursos',
            items: [
              { text: 'Visão Geral', link: '/pt/features' },
              { text: 'Extrator de Alias', link: '/pt/features/alias-extractor' },
              { text: 'Injetor de Atributos', link: '/pt/features/attribute-injector' },
              { text: 'Sincronização de Grupos OU', link: '/pt/features/ou-group-sync' }
            ]
          },
          {
            text: 'Ajuda',
            items: [
              { text: 'FAQ', link: '/pt/faq' },
              { text: 'Solução de Problemas', link: '/pt/troubleshooting' }
            ]
          }
        ],
        footer: {
          message: 'Lançado sob a Licença MIT.',
          copyright: 'Copyright © 2024 Colaboradores do GWorkspace Toolbox'
        }
      }
    }
  },

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'GWorkspace Toolbox',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/rafaelctz/GWorkspace-toolbox' }
    ],
    search: {
      provider: 'local'
    }
  }
})
