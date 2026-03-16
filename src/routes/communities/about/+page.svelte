<script lang="ts">
  import { env } from '$env/dynamic/public'
  import Header from '$lib/components/ui/layout/pages/Header.svelte'
  import { page } from '$app/stores'

  const COMMUNITY_CREATION_MIN_RATING = 10

  $: siteTitle = env.PUBLIC_SITE_TITLE || 'Comuna'
  $: title = `Что такое сообщества — ${siteTitle}`
  $: description =
    'Сообщества на Comuna: отдельные пространства вокруг продукта, команды или интереса с обсуждениями, беклогом и дорожной картой.'
  $: canonicalUrl = new URL(
    $page.url.pathname,
    (env.PUBLIC_SITE_URL || $page.url.origin).replace(/\/+$/, '') + '/'
  ).toString()

  const highlights = [
    {
      title: 'Один адрес для аудитории',
      copy: 'У сообщества есть собственная страница, которую можно отправлять пользователям, команде и партнерам.',
    },
    {
      title: 'Посты, обсуждения и roadmap',
      copy: 'Внутри можно собирать предложения, вести беклог, показывать, что в работе, и переносить лучшие идеи по этапам.',
    },
    {
      title: 'Порог на создание',
      copy: `Создать новое сообщество может автор с рейтингом выше ${COMMUNITY_CREATION_MIN_RATING}. Это снижает шум и защищает каталог от случайных пустых пространств.`,
    },
  ]

  const steps = [
    'Создатель открывает сообщество и настраивает описание, ссылки, категории и приветственный пост.',
    'Пользователи публикуют идеи и обсуждают изменения прямо в карточках постов.',
    'Команда переводит лучшие предложения в беклог и дорожную карту.',
    'Когда работа завершена, этапы и карточки остаются публичной историей продукта.',
  ]
</script>

<div class="community-landing">
  <section class="hero">
    <div class="hero__glow hero__glow--left"></div>
    <div class="hero__glow hero__glow--right"></div>
    <Header pageHeader>
      <div class="hero__copy">
        <div class="hero__eyebrow">Сообщества на Comuna</div>
        <h1>Публичное пространство вокруг продукта, команды или идеи</h1>
        <p>
          Сообщество объединяет ленту публикаций, обсуждения, предложения пользователей, беклог и дорожную карту.
          Это страница, которую можно смело отправлять вовне.
        </p>
        <div class="hero__actions">
          <a class="hero__button hero__button--primary" href="/comuns?create=1">Создать сообщество</a>
          <a class="hero__button" href="/faq">Открыть FAQ</a>
        </div>
      </div>
    </Header>
  </section>

  <section class="highlights">
    {#each highlights as item}
      <article class="panel">
        <div class="panel__label">{item.title}</div>
        <p>{item.copy}</p>
      </article>
    {/each}
  </section>

  <section class="details-grid">
    <article class="panel panel--wide">
      <div class="panel__label">Как это работает</div>
      <ol>
        {#each steps as step}
          <li>{step}</li>
        {/each}
      </ol>
    </article>

    <article class="panel">
      <div class="panel__label">Для кого это</div>
      <p>Для основателей, продуктовых команд, авторов, студий, клубов и любых проектов, которым нужен открытый контур обратной связи.</p>
    </article>

    <article class="panel">
      <div class="panel__label">Что увидят пользователи</div>
      <p>Описание проекта, ленту публикаций, дорожную карту, статусы задач и точку входа для предложений и обсуждений.</p>
    </article>
  </section>
</div>

<svelte:head>
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta property="og:title" content={title} />
  <meta property="og:description" content={description} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={canonicalUrl} />
  <link rel="canonical" href={canonicalUrl} />
</svelte:head>

<style>
  :global(:root) {
    --community-ink: #18233d;
    --community-muted: #60708c;
    --community-line: rgba(24, 35, 61, 0.12);
    --community-accent: #ff6a1a;
    --community-accent-soft: rgba(255, 106, 26, 0.14);
    --community-sky: #dceafe;
  }

  .community-landing {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    max-width: 72rem;
  }

  .hero {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--community-line);
    border-radius: 2rem;
    padding: 2rem;
    background:
      radial-gradient(circle at top left, rgba(146, 180, 255, 0.3), transparent 35%),
      radial-gradient(circle at top right, rgba(255, 182, 138, 0.28), transparent 36%),
      linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(244, 247, 255, 0.92));
    box-shadow: 0 24px 80px rgba(15, 23, 42, 0.08);
  }

  .hero__copy {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 42rem;
  }

  .hero__eyebrow,
  .panel__label {
    font-size: 0.8rem;
    line-height: 1;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--community-muted);
  }

  .hero h1 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3.5rem);
    line-height: 1.02;
    color: var(--community-ink);
  }

  .hero p,
  .panel p,
  .panel li {
    margin: 0;
    font-size: 1rem;
    line-height: 1.7;
    color: var(--community-muted);
  }

  .hero__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding-top: 0.25rem;
  }

  .hero__button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 3rem;
    padding: 0.75rem 1.2rem;
    border-radius: 999px;
    border: 1px solid var(--community-line);
    background: rgba(255, 255, 255, 0.78);
    color: var(--community-ink);
    text-decoration: none;
    font-weight: 600;
    transition:
      transform 0.18s ease,
      border-color 0.18s ease,
      background 0.18s ease;
  }

  .hero__button:hover {
    transform: translateY(-1px);
    border-color: rgba(24, 35, 61, 0.24);
  }

  .hero__button--primary {
    background: var(--community-accent);
    border-color: transparent;
    color: white;
  }

  .highlights,
  .details-grid {
    display: grid;
    gap: 1rem;
  }

  .highlights {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .details-grid {
    grid-template-columns: 1.3fr 1fr 1fr;
  }

  .panel {
    border: 1px solid var(--community-line);
    border-radius: 1.5rem;
    padding: 1.25rem;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 250, 255, 0.9));
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .panel--wide {
    grid-column: span 1;
  }

  ol {
    margin: 0;
    padding-left: 1.2rem;
    display: grid;
    gap: 0.75rem;
  }

  .hero__glow {
    position: absolute;
    border-radius: 999px;
    filter: blur(40px);
    opacity: 0.75;
    pointer-events: none;
  }

  .hero__glow--left {
    width: 14rem;
    height: 14rem;
    background: var(--community-sky);
    left: -4rem;
    top: -5rem;
  }

  .hero__glow--right {
    width: 16rem;
    height: 16rem;
    background: var(--community-accent-soft);
    right: -4rem;
    top: -4rem;
  }

  :global(.dark) .hero,
  :global(.dark) .panel {
    background:
      radial-gradient(circle at top left, rgba(76, 101, 155, 0.26), transparent 35%),
      radial-gradient(circle at top right, rgba(180, 102, 57, 0.22), transparent 36%),
      linear-gradient(135deg, rgba(27, 37, 58, 0.96), rgba(20, 25, 39, 0.94));
    border-color: rgba(176, 191, 223, 0.14);
    box-shadow: none;
  }

  :global(.dark) .hero h1,
  :global(.dark) .hero__button,
  :global(.dark) .panel__label {
    color: #f3f6ff;
  }

  :global(.dark) .hero p,
  :global(.dark) .panel p,
  :global(.dark) .panel li,
  :global(.dark) .hero__eyebrow {
    color: #b8c5e0;
  }

  :global(.dark) .hero__button {
    background: rgba(20, 25, 39, 0.78);
    border-color: rgba(176, 191, 223, 0.16);
  }

  :global(.dark) .hero__button--primary {
    background: var(--community-accent);
    color: white;
    border-color: transparent;
  }

  @media (max-width: 900px) {
    .hero {
      padding: 1.5rem;
      border-radius: 1.5rem;
    }

    .highlights,
    .details-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
