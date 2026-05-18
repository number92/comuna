<script lang="ts">
  import { onMount } from 'svelte'
  import { Button, toast } from 'mono-svelte'
  import {
    buildSpecial1001FilmsResumeUrl,
    buildSpecial1001FilmsStartUrl,
    buildSpecial1001FilmsStatusUrl,
  } from '$lib/api/backend'
  import LoginModal from '$lib/components/auth/LoginModal.svelte'
  import TelegramLoginButton from '$lib/components/telegram/TelegramLoginButton.svelte'
  import { refreshSiteUser, siteToken, siteUser } from '$lib/siteAuth'
  import {
    ArrowPath,
    CalendarDays,
    CheckCircle,
    Film,
    Icon,
    LockClosed,
    Play,
  } from 'svelte-hero-icons'

  type FilmJourneyEntry = {
    position: number
    path: string
    completed_at?: string | null
    film?: {
      title: string
      original_title?: string
      year?: number
      category?: string
    }
  }

  type FilmJourneySubscription = {
    status: 'active' | 'paused' | 'completed'
    next_delivery_at: string
    completed_count: number
    total_count: number
    pause_reason?: string
    current_entry?: FilmJourneyEntry | null
  }

  type FilmJourneyStatus = {
    ok: boolean
    total_count: number
    landing_images?: LandingImage[]
    subscription?: FilmJourneySubscription | null
  }

  type LandingImage = {
    slot: string
    title: string
    image_url: string
  }

  let status: FilmJourneyStatus | null = null
  let loading = true
  let actionLoading = false
  let error = ''
  let authOpen = false
  let telegramPromptOpen = false

  const authHeaders = (): Record<string, string> =>
    $siteToken ? { Authorization: `Bearer ${$siteToken}` } : {}

  async function loadStatus() {
    loading = true
    error = ''
    try {
      const response = await fetch(buildSpecial1001FilmsStatusUrl(), {
        credentials: 'include',
        headers: authHeaders(),
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        throw new Error(data?.error || 'Не удалось загрузить спецпроект')
      }
      status = data
    } catch (err) {
      error = (err as Error)?.message || 'Не удалось загрузить спецпроект'
    }
    loading = false
  }

  async function postAction(url: string, successMessage = 'Готово') {
    if (!$siteToken) {
      authOpen = true
      return
    }
    actionLoading = true
    try {
      const response = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: authHeaders(),
      })
      const data = await response.json()
      if (!response.ok || !data?.ok) {
        throw new Error(data?.error || 'Не удалось выполнить действие')
      }
      status = {
        ok: true,
        total_count: data.subscription?.total_count ?? status?.total_count ?? 0,
        subscription: data.subscription,
      }
      toast({ content: successMessage, type: 'success' })
    } catch (err) {
      toast({ content: (err as Error)?.message || 'Не удалось выполнить действие', type: 'error' })
    }
    actionLoading = false
  }

  async function startJourney() {
    if (!$siteToken || !$siteUser) {
      authOpen = true
      return
    }
    if (!$siteUser.telegram_linked) {
      telegramPromptOpen = true
      toast({
        content: 'Фильмы будут приходить в Telegram-бота и на сайт. Давайте сначала привяжем Telegram.',
        type: 'info',
      })
      return
    }
    await postAction(
      buildSpecial1001FilmsStartUrl(),
      'Маршрут запущен. Оповещения будут приходить в Telegram-бота и на сайт.',
    )
  }

  async function resumeJourney() {
    if (!$siteToken || !$siteUser) {
      authOpen = true
      return
    }
    if (!$siteUser.telegram_linked) {
      telegramPromptOpen = true
      toast({
        content: 'Чтобы продолжить с оповещениями, давайте привяжем Telegram.',
        type: 'info',
      })
      return
    }
    await postAction(
      buildSpecial1001FilmsResumeUrl(),
      'Маршрут возобновлен. Оповещения будут приходить в Telegram-бота и на сайт.',
    )
  }

  async function handleTelegramLinked() {
    await refreshSiteUser()
    telegramPromptOpen = false
    toast({
      content: 'Telegram привязан. Теперь можно начать маршрут и получать фильм дня в боте.',
      type: 'success',
    })
  }

  const formatDate = (value?: string | null) => {
    if (!value) return ''
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(value))
  }

  $: subscription = status?.subscription ?? null
  $: currentEntry = subscription?.current_entry ?? null
  $: progressLabel = subscription
    ? `${subscription.completed_count} из 1001`
    : '0 из 1001'
  $: landingImages = ['1', '2', '3'].map((slot) => {
    return (
      status?.landing_images?.find((image) => image.slot === slot) ?? {
        slot,
        title: `Кадр ${slot}`,
        image_url: '',
      }
    )
  })
  $: heroImage = landingImages.find((image) => image.image_url) ?? landingImages[0]

  onMount(loadStatus)
</script>

<svelte:head>
  <title>1001 фильм, который должен посмотреть каждый</title>
  <meta
    name="description"
    content="Спецпроект Tambur: один фильм в день, секретные ссылки и общий порядок для всех участников."
  />
  <link rel="canonical" href="/s/1001-films" />
</svelte:head>

<LoginModal bind:open={authOpen} initialMode="signup" />

<section class="films-page">
  <div class="hero-shapes" aria-hidden="true">
    <span></span>
    <span></span>
    <span></span>
  </div>
  <div class="hero">
    <div class="hero-copy">
      <h1>1001 фильм, который должен посмотреть каждый</h1>
      <p class="lead">
        Каждый день вы получаете один фильм, только посмотрев и оценив его вы переходите
        к следующему, пропускать нельзя, выбирать нельзя — погрузиться в мир разных жанров,
        культур и эпох — нужно!
      </p>
      <div class="actions">
        {#if loading}
          <Button size="lg" disabled>
            <Icon src={ArrowPath} size="18" mini slot="prefix" />
            Загрузка
          </Button>
        {:else if !$siteToken || !$siteUser}
          <Button size="lg" color="primary" on:click={() => (authOpen = true)}>
            <Icon src={LockClosed} size="18" mini slot="prefix" />
            Зарегистрироваться и начать
          </Button>
        {:else if !subscription}
          <Button
            size="lg"
            color="primary"
            loading={actionLoading}
            disabled={actionLoading}
            on:click={startJourney}
          >
            <Icon src={Play} size="18" mini slot="prefix" />
            Начать путешествие
          </Button>
        {:else if subscription.status === 'paused'}
          <Button
            size="lg"
            color="primary"
            loading={actionLoading}
            disabled={actionLoading}
            on:click={resumeJourney}
          >
            <Icon src={Play} size="18" mini slot="prefix" />
            Возобновить
          </Button>
        {:else if currentEntry && !currentEntry.completed_at}
          <Button size="lg" color="primary" href={currentEntry.path}>
            <Icon src={Film} size="18" mini slot="prefix" />
            Открыть текущий фильм
          </Button>
        {:else if subscription.status === 'completed'}
          <Button size="lg" disabled>
            <Icon src={CheckCircle} size="18" mini slot="prefix" />
            Маршрут завершён
          </Button>
        {:else}
          <Button size="lg" disabled>
            <Icon src={CalendarDays} size="18" mini slot="prefix" />
            Следующий фильм {formatDate(subscription.next_delivery_at)}
          </Button>
        {/if}
        {#if $siteUser?.is_staff}
          <Button size="lg" href="/s/1001-films/admin">
            Управление фильмами
          </Button>
        {/if}
      </div>
      {#if $siteUser?.telegram_linked && !subscription}
        <p class="notification-note">
          После старта фильм дня будет приходить в Telegram-бота и в уведомления на сайте.
        </p>
      {/if}
      {#if telegramPromptOpen && $siteUser && !$siteUser.telegram_linked}
        <div class="telegram-callout">
          <div>
            <strong>Привяжем Telegram для оповещений</strong>
            <p>
              Секретная ссылка на новый фильм придет в Telegram-бота и останется в уведомлениях на сайте.
            </p>
          </div>
          <TelegramLoginButton
            label="Связать Telegram"
            helperText="Нужно для ежедневных ссылок и напоминаний"
            authIntent="login"
            privacyAccepted={false}
            active={telegramPromptOpen}
            onSuccess={handleTelegramLinked}
          />
        </div>
      {/if}
      {#if error}
        <p class="error">{error}</p>
      {/if}
    </div>

    <div class="project-panel" aria-label="Статус проекта">
      <div class="editorial-visual" class:has-image={Boolean(heroImage?.image_url)}>
        {#if heroImage?.image_url}
          <img src={heroImage.image_url} alt={heroImage.title || 'Кадр из фильма'} loading="lazy" />
        {:else}
          <div class="visual-placeholder" aria-hidden="true"></div>
        {/if}
      </div>
      <div class="panel-grid">
        <div>
          <span>Прогресс</span>
          <strong>{progressLabel}</strong>
        </div>
      </div>
      {#if subscription}
        <div class="status-line">
          {#if subscription.status === 'paused'}
            Пауза: {subscription.pause_reason || 'ждём оценки текущего фильма'}
          {:else if subscription.status === 'completed'}
            Все доступные фильмы пройдены.
          {:else if currentEntry && !currentEntry.completed_at}
            Сейчас открыт фильм #{currentEntry.position}: {currentEntry.film?.title}
          {:else}
            Следующая выдача запланирована на {formatDate(subscription.next_delivery_at)}.
          {/if}
        </div>
      {:else}
        <div class="status-line">Каждый участник идет по одному общему маршруту.</div>
      {/if}
    </div>
  </div>
</section>

<section class="how-it-works">
  <div class="how-inner">
    <div class="how-heading">
      <p>
        Это не каталог и не рейтинг. У всех участников один и тот же порядок фильмов,
        а доступ открывается постепенно: один день, один фильм, одна короткая реакция.
        Фильмы подобрали критики из сообщества
        <a href="https://tambur.pub/comuns/after_the_credits">«После титров»</a>.
      </p>
    </div>

    <div class="steps">
      <article class="step">
        <span class="step-icon">
          <Icon src={Play} size="18" mini />
        </span>
        <h3>Стартуете подписку</h3>
        <p>Нужно зарегистрироваться и подключить телеграм бота, чтобы мы могли отправлять вам новые фильмы. Это бесплатно.</p>
      </article>
      <article class="step">
        <span class="step-icon">
          <Icon src={CalendarDays} size="18" mini />
        </span>
        <h3>Получаете фильм дня</h3>
        <p>Раз в сутки приходит информация, какой фильм вам нужно посмотреть, и краткое описание. Вы смотрите этот фильм.</p>
      </article>
      <article class="step">
        <span class="step-icon">
          <Icon src={CheckCircle} size="18" mini />
        </span>
        <h3>Оцениваете и комментируете</h3>
        <p>
          Вы ставите оценку фильму, комментируете, читаете мнение сообщества,
          обсуждаете и после этого на следующий день получите ссылку на новый.
        </p>
      </article>
    </div>

    <div class="rules">
      <p>
        Если фильм завис без реакции, через пару дней придёт напоминание, потом ещё одно.
        После этого подписка ставится на паузу. Вернуться можно в любой момент: проект продолжит
        с того места, где вы остановились.
      </p>
    </div>

    <div class="faq" aria-label="Частые вопросы">
      <details>
        <summary>Я могу посмотреть фильм у вас на сайте?</summary>
        <p>
          Нет, мы только предоставляем сервис выдающий вам список фильмов для просмотра.
          Мы не даем сами фильмы, но они без проблем доступны в интернете.
        </p>
      </details>
      <details>
        <summary>Это бесплатно?</summary>
        <p>Да, сервис полностью бесплатен и не содержит никаких рекламных элементов.</p>
      </details>
      <details>
        <summary>У меня займет посмотреть все фильмы около 2,5 лет?</summary>
        <p>
          Да, это большое кинопутешествие, но вы можете делать паузы и возвращаться к нему
          когда будет настроение.
        </p>
      </details>
      <details>
        <summary>Какие фильмы я смогу увидеть в списке?</summary>
        <p>
          Критики подобрали фильмы абсолютно разных жанров, эпох и школ. Мы постарались собрать
          список, чтобы он не пересекался с известными топами, то есть тут будут преимущественно
          другие фильмы, но более интересные!
        </p>
      </details>
      <details>
        <summary>Зачем мне этот список?</summary>
        <p>
          Это интересный опыт, когда вы не выбираете фильм совсем, только выбираете смотреть его
          сегодня или нет. А наш призыв дать комментарий про фильм в конце дает вам ощущение более
          вдумчивого просмотра. Этот список для любителей кино и возможность погрузиться в
          увлекательное путешествие.
        </p>
      </details>
    </div>
  </div>
</section>

<style>
  .films-page {
    --retro-night: #17164a;
    --retro-panel: #24205f;
    --retro-panel-strong: #101044;
    --retro-orange: #ff5a37;
    --retro-gold: #ffc15e;
    --retro-cyan: #26d7d0;
    --retro-cream: #fff2d4;
    --retro-paper: #f5d8b0;
    --retro-muted: #c9b6cf;
    --retro-line: rgb(255 242 212 / 0.18);
    --btn-primary-background: var(--retro-orange);
    --btn-primary-background-hover: #ff704f;
    --btn-primary-color: #fff8e8;
    --btn-primary-shadow: 0 0.55rem 1.1rem rgb(255 90 55 / 0.28);
    --btn-primary-shadow-hover: 0 0.7rem 1.35rem rgb(255 90 55 / 0.36);

    position: relative;
    overflow: hidden;
    min-height: auto;
    margin-top: -1rem;
    background:
      radial-gradient(circle at 16% 12%, rgb(255 193 94 / 0.24), transparent 16rem),
      radial-gradient(circle at 88% 18%, rgb(38 215 208 / 0.22), transparent 18rem),
      radial-gradient(circle at 50% 110%, rgb(255 90 55 / 0.18), transparent 22rem),
      linear-gradient(180deg, #403494 0, #2a2376 46%, #1e1c63 100%);
    color: var(--retro-cream);
    padding: clamp(1rem, 2.2vw, 1.6rem) clamp(1rem, 4vw, 3rem) clamp(1rem, 2vw, 1.6rem);
    display: flex;
    align-items: flex-start;
  }

  .films-page::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle, rgb(255 242 212 / 0.42) 0 0.06rem, transparent 0.08rem) 0.35rem 0.45rem / 2.6rem 2.25rem,
      linear-gradient(140deg, transparent 0 42%, rgb(255 255 255 / 0.05) 42% 43%, transparent 43% 100%);
    opacity: 0.34;
  }

  .hero-shapes {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .hero-shapes span {
    position: absolute;
    border-radius: 999px;
    opacity: 0.9;
  }

  .hero-shapes span:nth-child(1) {
    width: 19rem;
    height: 19rem;
    right: max(1rem, calc(50% - 38rem));
    top: 1.2rem;
    background:
      radial-gradient(circle at 32% 26%, rgb(255 242 212 / 0.2), transparent 2.4rem),
      radial-gradient(circle at 64% 58%, rgb(16 16 68 / 0.22), transparent 3.2rem),
      linear-gradient(135deg, #7469c9, #4091c8);
    box-shadow: inset -1.5rem -1.5rem 0 rgb(19 18 76 / 0.22);
  }

  .hero-shapes span:nth-child(2) {
    width: 42rem;
    height: 42rem;
    left: max(-10rem, calc(50% - 50rem));
    bottom: -30rem;
    border: 1.2rem solid rgb(255 90 55 / 0.18);
    border-radius: 999px;
    background:
      radial-gradient(circle, transparent 0 62%, rgb(38 215 208 / 0.12) 63% 64%, transparent 65%);
  }

  .hero-shapes span:nth-child(3) {
    width: 0.95rem;
    height: 0.95rem;
    left: max(2rem, calc(50% - 5rem));
    top: 5.5rem;
    border-radius: 0;
    background: var(--retro-gold);
    box-shadow:
      0 0 0 0.45rem rgb(255 193 94 / 0.14),
      17rem 7rem 0 -0.1rem var(--retro-gold),
      24rem 17rem 0 -0.25rem var(--retro-orange),
      -16rem 14rem 0 -0.2rem var(--retro-cyan);
    transform: rotate(45deg);
  }

  .hero {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(18rem, 25.5rem);
    gap: clamp(1.25rem, 4vw, 3rem);
    align-items: end;
    max-width: 70rem;
    width: 100%;
    margin: 0 auto;
    border: 1px solid rgb(255 242 212 / 0.13);
    border-radius: 2rem;
    background:
      radial-gradient(circle at 72% 18%, rgb(64 145 200 / 0.24), transparent 15rem),
      linear-gradient(135deg, rgb(18 17 76 / 0.86), rgb(36 32 95 / 0.82));
    padding: clamp(1.1rem, 3vw, 2.4rem);
    box-shadow: 0 1.4rem 4rem rgb(16 16 68 / 0.28);
  }

  .hero-copy {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  h1 {
    max-width: 13ch;
    font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
    font-size: clamp(2.45rem, 6vw, 6.35rem);
    line-height: 0.9;
    letter-spacing: 0;
    font-weight: 900;
    text-transform: uppercase;
    color: var(--retro-orange);
    text-wrap: balance;
    text-shadow: 0.08em 0.08em 0 rgb(16 16 68 / 0.48);
  }

  .lead {
    max-width: 42rem;
    color: var(--retro-cream);
    font-size: clamp(0.98rem, 1.5vw, 1.08rem);
    line-height: 1.55;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 0.25rem;
  }

  .error {
    color: #ffe0a6;
  }

  .notification-note {
    max-width: 35rem;
    color: var(--retro-muted);
    font-size: 0.92rem;
    line-height: 1.45;
  }

  .telegram-callout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(16rem, 20rem);
    gap: 0.8rem;
    align-items: center;
    max-width: 42rem;
    border: 1px solid rgb(38 215 208 / 0.32);
    border-radius: 1.2rem;
    background: rgb(16 16 68 / 0.44);
    padding: 0.85rem;
    box-shadow: inset 0 0 0 1px rgb(255 242 212 / 0.08);
    backdrop-filter: blur(16px);
  }

  .telegram-callout strong {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
    color: var(--retro-cream);
  }

  .telegram-callout p {
    color: var(--retro-muted);
    font-size: 0.9rem;
    line-height: 1.45;
  }

  .project-panel {
    position: relative;
    overflow: hidden;
    border: 1px solid rgb(255 242 212 / 0.18);
    border-radius: 1.7rem;
    background:
      radial-gradient(circle at 56% 20%, rgb(38 215 208 / 0.2), transparent 11rem),
      linear-gradient(180deg, rgb(255 242 212 / 0.12), rgb(255 242 212 / 0.04)),
      rgb(36 32 95 / 0.76);
    padding: 0.72rem;
    box-shadow: 0 1.4rem 3.4rem rgb(16 16 68 / 0.34);
    backdrop-filter: blur(18px);
  }

  .project-panel::before {
    content: "";
    position: absolute;
    inset: 0.72rem;
    border: 1px solid rgb(255 242 212 / 0.16);
    border-radius: 1.25rem;
    pointer-events: none;
  }

  .editorial-visual {
    position: relative;
    min-height: clamp(15rem, 46svh, 28rem);
    margin-bottom: 0.9rem;
    overflow: hidden;
    border-radius: 1.2rem;
    background:
      radial-gradient(circle at 68% 28%, #536ec5 0 4.4rem, transparent 4.55rem),
      radial-gradient(circle at 74% 30%, rgb(255 242 212 / 0.12), transparent 8rem),
      radial-gradient(circle at 28% 80%, rgb(255 90 55 / 0.42), transparent 9rem),
      linear-gradient(145deg, #211c6b, #15164f 64%);
  }

  .editorial-visual::before,
  .editorial-visual::after {
    content: "";
    position: absolute;
    pointer-events: none;
    z-index: 2;
  }

  .editorial-visual::before {
    inset: 1rem;
    border: 1px solid rgb(255 242 212 / 0.24);
    border-radius: 0.95rem;
  }

  .editorial-visual::after {
    inset: 0;
    background:
      radial-gradient(circle, rgb(255 242 212 / 0.48) 0 0.045rem, transparent 0.075rem) 0.4rem 0.6rem / 2.4rem 2rem,
      linear-gradient(180deg, transparent 48%, rgb(16 16 68 / 0.38));
  }

  .editorial-visual.has-image {
    background: #15164f;
  }

  .editorial-visual img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: saturate(1.12) contrast(1.05) sepia(0.12);
  }

  .visual-placeholder {
    position: absolute;
    inset: 0;
    background:
      conic-gradient(from 22deg at 50% 104%, rgb(255 90 55 / 0.95), rgb(255 193 94 / 0.9), transparent 22deg 338deg, rgb(255 90 55 / 0.95)),
      radial-gradient(circle at 70% 28%, #596fc4 0 4.8rem, transparent 5rem),
      radial-gradient(circle at 78% 36%, rgb(16 16 68 / 0.22) 0 1.2rem, transparent 1.3rem),
      linear-gradient(145deg, #272178, #15164f 68%);
  }

  .visual-placeholder::before {
    content: "";
    position: absolute;
    left: 47%;
    top: 12%;
    width: min(44%, 10rem);
    aspect-ratio: 0.56;
    border: 0.18rem solid #141447;
    border-radius: 58% 58% 20% 20%;
    transform: translateX(-50%) rotate(11deg);
    background:
      linear-gradient(90deg, transparent 0 24%, #141447 24% 27%, transparent 27% 73%, #141447 73% 76%, transparent 76%),
      radial-gradient(circle at 50% 20%, #ff5a37 0 1.4rem, transparent 1.48rem),
      linear-gradient(90deg, #f6e1ad, #b6b1ad 50%, #f6e1ad);
    box-shadow:
      -3.1rem 7.5rem 0 -2.1rem #f6e1ad,
      3.1rem 7.5rem 0 -2.1rem #f6e1ad,
      0 12.5rem 0 -3.2rem #ff5a37;
  }

  .visual-placeholder::after {
    content: "";
    position: absolute;
    left: 18%;
    bottom: 13%;
    width: 48%;
    height: 0.62rem;
    border-radius: 999px;
    background: #26d7d0;
    box-shadow:
      1.5rem 1.2rem 0 #ff5a37,
      4.4rem -1.25rem 0 -0.12rem #ffc15e;
    transform: rotate(-5deg);
  }

  .panel-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.55rem;
  }

  .panel-grid div {
    border-radius: 1rem;
    background: rgb(16 16 68 / 0.42);
    border: 1px solid rgb(38 215 208 / 0.26);
    padding: 0.7rem 0.8rem;
  }

  .panel-grid span,
  .status-line {
    color: var(--retro-muted);
    font-size: 0.9rem;
  }

  .panel-grid strong {
    display: block;
    margin-top: 0.18rem;
    font-size: 1.45rem;
    font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
    font-weight: 900;
    color: var(--retro-cyan);
    letter-spacing: 0;
  }

  .status-line {
    margin-top: 0.75rem;
    line-height: 1.45;
  }

  .how-it-works {
    --retro-night: #17164a;
    --retro-panel: #24205f;
    --retro-orange: #ff5a37;
    --retro-gold: #ffc15e;
    --retro-cyan: #139fba;
    --retro-cream: #fff2d4;
    --retro-paper: #2a254b;
    --retro-muted: #685c7a;
    --retro-line: rgb(42 37 75 / 0.16);

    background:
      radial-gradient(circle at 12% 8%, rgb(255 193 94 / 0.28), transparent 18rem),
      radial-gradient(circle at 86% 18%, rgb(38 215 208 / 0.18), transparent 16rem),
      linear-gradient(90deg, transparent 0 calc(100% - 1px), rgb(42 37 75 / 0.055) calc(100% - 1px)) 0 0 / 4rem 100%,
      linear-gradient(180deg, #f4dcae, #f8ead0 34%, #f3d7a4);
    color: var(--retro-paper);
    border-top: 1px solid rgb(255 242 212 / 0.18);
    padding: clamp(0.65rem, 1.5vw, 1.2rem) clamp(1rem, 4vw, 3rem) clamp(2rem, 5vw, 4.5rem);
  }

  .how-inner {
    max-width: 70rem;
    margin: 0 auto;
  }

  .how-heading {
    max-width: 54rem;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    border-left: 0.35rem solid var(--retro-orange);
    padding-left: 1.2rem;
  }

  .how-heading p,
  .step p,
  .rules p,
  .faq p {
    color: var(--retro-paper);
    line-height: 1.6;
  }

  .how-heading a {
    color: #087eaa;
    font-weight: 700;
    text-decoration: underline;
    text-underline-offset: 0.16em;
    text-decoration-color: rgb(255 90 55 / 0.58);
  }

  .steps {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.85rem;
    margin-top: clamp(0.8rem, 2vw, 1.35rem);
  }

  .step {
    position: relative;
    overflow: hidden;
    border: 1px solid rgb(42 37 75 / 0.14);
    border-radius: 1.1rem;
    background: rgb(255 242 212 / 0.58);
    padding: 1.05rem;
    box-shadow: 0 0.7rem 1.6rem rgb(42 37 75 / 0.08);
  }

  .step::before {
    content: "";
    position: absolute;
    inset: 0 0 auto;
    height: 0.35rem;
    background: linear-gradient(90deg, var(--retro-orange), var(--retro-gold), transparent);
  }

  .step:nth-child(1) {
    background: linear-gradient(160deg, rgb(255 90 55 / 0.18), rgb(255 242 212 / 0.72) 58%);
  }

  .step:nth-child(2) {
    background: linear-gradient(160deg, rgb(38 215 208 / 0.18), rgb(255 242 212 / 0.72) 58%);
  }

  .step:nth-child(3) {
    background: linear-gradient(160deg, rgb(255 193 94 / 0.22), rgb(255 242 212 / 0.72) 58%);
  }

  .step:nth-child(1)::before {
    background: linear-gradient(90deg, var(--retro-orange), transparent);
  }

  .step:nth-child(3)::before {
    background: linear-gradient(90deg, var(--retro-gold), transparent);
  }

  .step-icon {
    width: 2rem;
    height: 2rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    color: #101044;
    background: var(--retro-gold);
    border: 2px solid rgb(42 37 75 / 0.12);
    margin-bottom: 0.9rem;
  }

  .step:nth-child(1) .step-icon {
    color: #101044;
    background: var(--retro-orange);
  }

  .step:nth-child(2) .step-icon {
    color: #101044;
    background: #26d7d0;
  }

  .step:nth-child(3) .step-icon {
    color: #101044;
  }

  .step h3 {
    font-size: 1.05rem;
    font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
    font-weight: 900;
    margin-bottom: 0.45rem;
    color: #17164a;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  .rules {
    margin-top: 0.85rem;
    border-radius: 1.1rem;
    border: 1px solid rgb(42 37 75 / 0.14);
    padding: 1rem 1.1rem;
    background:
      linear-gradient(90deg, rgb(255 90 55 / 0.13), transparent),
      rgb(255 242 212 / 0.58);
    box-shadow: 0 0.7rem 1.6rem rgb(42 37 75 / 0.07);
  }

  .faq {
    margin-top: 1rem;
    display: grid;
    gap: 0.6rem;
  }

  .faq details {
    border: 1px solid rgb(42 37 75 / 0.14);
    border-radius: 1rem;
    background: rgb(255 242 212 / 0.56);
    padding: 0.9rem 1rem;
    box-shadow: 0 0.5rem 1.25rem rgb(42 37 75 / 0.06);
  }

  .faq details:nth-child(3n + 1) {
    background: rgb(255 90 55 / 0.12);
  }

  .faq details:nth-child(3n + 2) {
    background: rgb(38 215 208 / 0.14);
  }

  .faq details:nth-child(3n + 3) {
    background: rgb(255 193 94 / 0.16);
  }

  .faq details[open] {
    border-color: rgb(255 90 55 / 0.36);
    background: rgb(255 242 212 / 0.78);
  }

  .faq summary {
    cursor: pointer;
    color: #17164a;
    font-size: 1rem;
    font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
    font-weight: 900;
    line-height: 1.35;
    letter-spacing: 0;
    text-transform: uppercase;
  }

  .faq summary::marker {
    color: var(--retro-orange);
  }

  .faq p {
    margin-top: 0.65rem;
  }

  @media (max-width: 820px) {
    .films-page {
      min-height: auto;
      align-items: flex-start;
      padding: 1.35rem 1rem 1.5rem;
    }

    .hero {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    h1 {
      max-width: 18ch;
      font-size: clamp(1.55rem, 5.46vw, 2.07rem);
      line-height: 1.02;
    }

    .lead {
      font-size: 0.94rem;
      line-height: 1.45;
    }

    .editorial-visual {
      min-height: min(44svh, 20rem);
    }

    .project-panel {
      padding: 0.7rem;
    }

    .panel-grid div {
      padding: 0.55rem 0.65rem;
    }

    .panel-grid strong {
      font-size: 1.18rem;
    }

    .status-line {
      font-size: 0.82rem;
      margin-top: 0.55rem;
    }

    .telegram-callout {
      grid-template-columns: 1fr;
    }

    .how-it-works {
      padding: 2rem 1rem;
    }

    .how-heading {
      padding-left: 0.8rem;
    }

    .steps {
      grid-template-columns: 1fr;
    }
  }

  @media (min-width: 560px) and (max-width: 820px) {
    .films-page {
      align-items: center;
    }

    .hero {
      grid-template-columns: minmax(0, 1fr) 13.5rem;
      gap: 1rem;
    }

    h1 {
      max-width: 16ch;
      font-size: clamp(1.44rem, 4.25vw, 1.84rem);
    }

    .lead {
      max-width: 30rem;
      font-size: 0.9rem;
    }

    .editorial-visual {
      min-height: min(38svh, 16rem);
    }
  }
</style>
