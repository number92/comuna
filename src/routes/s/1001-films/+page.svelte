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
    --editorial-ink: #f4ead7;
    --editorial-paper: #d8c5a7;
    --editorial-muted: #9c8d78;
    --editorial-bg: #12100e;
    --editorial-copper: #b06b3f;
    --editorial-wine: #5e1f20;
    --editorial-olive: #29372b;
    --editorial-line: rgb(244 234 215 / 0.2);

    position: relative;
    overflow: hidden;
    min-height: auto;
    margin-top: -1rem;
    background:
      radial-gradient(circle at 78% 12%, rgb(176 107 63 / 0.28), transparent 17rem),
      radial-gradient(circle at 12% 78%, rgb(94 31 32 / 0.34), transparent 18rem),
      linear-gradient(90deg, rgb(244 234 215 / 0.04) 1px, transparent 1px) 0 0 / 4.25rem 100%,
      linear-gradient(135deg, #17130f 0, #0f0e0c 48%, #201611 100%);
    color: var(--editorial-ink);
    padding: clamp(1rem, 2.2vw, 1.8rem) clamp(1rem, 4vw, 3rem) clamp(1.2rem, 2vw, 2rem);
    display: flex;
    align-items: flex-start;
  }

  .films-page::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle, rgb(244 234 215 / 0.13) 0 0.055rem, transparent 0.075rem) 0.25rem 0.25rem / 0.85rem 0.85rem,
      linear-gradient(rgb(244 234 215 / 0.06), transparent 0.16rem) 0 0 / 100% 0.52rem;
    opacity: 0.22;
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
    width: 20rem;
    height: 20rem;
    left: max(1rem, calc(50% - 34rem));
    top: -10rem;
    border: 1px solid var(--editorial-line);
    background: radial-gradient(circle, transparent 0 54%, rgb(176 107 63 / 0.16) 55% 56%, transparent 57%);
    transform: none;
  }

  .hero-shapes span:nth-child(2) {
    width: 11rem;
    height: 16rem;
    right: max(0.5rem, calc(50% - 37rem));
    bottom: -7rem;
    border: 1px solid rgb(244 234 215 / 0.16);
    border-radius: 999px 999px 0 0;
    background:
      linear-gradient(90deg, transparent 49%, rgb(244 234 215 / 0.18) 49% 51%, transparent 51%),
      linear-gradient(rgb(176 107 63 / 0.12), transparent);
    transform: rotate(10deg);
  }

  .hero-shapes span:nth-child(3) {
    width: 34rem;
    height: 1px;
    right: max(2rem, calc(50% - 32rem));
    top: 4rem;
    border-radius: 0;
    background: linear-gradient(90deg, transparent, rgb(244 234 215 / 0.5), transparent);
    transform: none;
  }

  .hero {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(18rem, 25.5rem);
    gap: clamp(1.25rem, 4vw, 3.5rem);
    align-items: end;
    max-width: 70rem;
    width: 100%;
    margin: 0 auto;
  }

  .hero-copy {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  h1 {
    max-width: 14ch;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(2.45rem, 5.6vw, 5.85rem);
    line-height: 0.88;
    letter-spacing: 0;
    font-weight: 400;
    color: var(--editorial-ink);
    text-wrap: balance;
    text-shadow: none;
  }

  .lead {
    max-width: 42rem;
    color: var(--editorial-paper);
    font-size: clamp(0.98rem, 1.5vw, 1.08rem);
    line-height: 1.65;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 0.25rem;
  }

  .error {
    color: #b91c1c;
  }

  .notification-note {
    max-width: 35rem;
    color: var(--editorial-muted);
    font-size: 0.92rem;
    line-height: 1.45;
  }

  .telegram-callout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(16rem, 20rem);
    gap: 0.8rem;
    align-items: center;
    max-width: 42rem;
    border: 1px solid var(--editorial-line);
    border-radius: 0;
    background: rgb(244 234 215 / 0.07);
    padding: 0.85rem;
    backdrop-filter: blur(18px);
  }

  .telegram-callout strong {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
    color: var(--editorial-ink);
  }

  .telegram-callout p {
    color: var(--editorial-paper);
    font-size: 0.9rem;
    line-height: 1.45;
  }

  .project-panel {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--editorial-line);
    border-radius: 0;
    background:
      linear-gradient(180deg, rgb(244 234 215 / 0.1), rgb(244 234 215 / 0.035)),
      rgb(18 16 14 / 0.76);
    padding: 0.85rem;
    box-shadow: 0 2rem 5rem rgb(0 0 0 / 0.34);
    backdrop-filter: blur(22px);
  }

  .project-panel::before {
    content: "";
    position: absolute;
    inset: 0.85rem;
    border: 1px solid rgb(244 234 215 / 0.18);
    pointer-events: none;
  }

  .editorial-visual {
    position: relative;
    min-height: clamp(16rem, 48svh, 30rem);
    margin-bottom: 0.9rem;
    overflow: hidden;
    background:
      radial-gradient(circle at 50% 31%, rgb(216 197 167 / 0.24), transparent 7rem),
      linear-gradient(145deg, #251813, #0f0e0c 62%);
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
    border: 1px solid rgb(244 234 215 / 0.34);
  }

  .editorial-visual::after {
    inset: 0;
    background:
      linear-gradient(180deg, transparent 48%, rgb(15 14 12 / 0.72)),
      radial-gradient(circle at 50% 42%, transparent 0 9rem, rgb(15 14 12 / 0.48) 15rem);
  }

  .editorial-visual.has-image {
    background: #0f0e0c;
  }

  .editorial-visual img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: saturate(0.78) contrast(1.08) sepia(0.18);
  }

  .visual-placeholder {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse at 50% 34%, rgb(216 197 167 / 0.3) 0 8rem, transparent 8.2rem),
      linear-gradient(90deg, transparent 48%, rgb(216 197 167 / 0.26) 48% 52%, transparent 52%),
      radial-gradient(ellipse at 50% 70%, rgb(176 107 63 / 0.32) 0 7rem, transparent 7.2rem),
      linear-gradient(145deg, #271815, #0f0e0c 66%);
  }

  .visual-placeholder::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 18%;
    width: min(46%, 11rem);
    aspect-ratio: 0.72;
    border: 1px solid rgb(244 234 215 / 0.38);
    border-radius: 999px 999px 18% 18%;
    transform: translateX(-50%);
    background:
      linear-gradient(90deg, transparent 47%, rgb(244 234 215 / 0.28) 47% 53%, transparent 53%),
      radial-gradient(circle at 50% 30%, rgb(244 234 215 / 0.2), transparent 4.5rem);
  }

  .panel-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.55rem;
  }

  .panel-grid div {
    border-radius: 0;
    background: rgb(244 234 215 / 0.08);
    border: 1px solid var(--editorial-line);
    padding: 0.7rem 0.8rem;
  }

  .panel-grid span,
  .status-line {
    color: var(--editorial-muted);
    font-size: 0.9rem;
  }

  .panel-grid strong {
    display: block;
    margin-top: 0.18rem;
    font-size: 1.45rem;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 400;
    color: var(--editorial-ink);
  }

  .status-line {
    margin-top: 0.75rem;
    line-height: 1.45;
  }

  .how-it-works {
    --editorial-ink: #f4ead7;
    --editorial-paper: #d8c5a7;
    --editorial-muted: #9c8d78;
    --editorial-bg: #12100e;
    --editorial-copper: #b06b3f;
    --editorial-wine: #5e1f20;
    --editorial-line: rgb(244 234 215 / 0.18);

    background:
      radial-gradient(circle at 18% 12%, rgb(176 107 63 / 0.2), transparent 17rem),
      linear-gradient(90deg, transparent 0 calc(100% - 1px), rgb(244 234 215 / 0.045) calc(100% - 1px)) 0 0 / 4.25rem 100%,
      linear-gradient(180deg, #15120f, #0f0e0c);
    color: var(--editorial-ink);
    border-top: 1px solid var(--editorial-line);
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
    border-left: 1px solid var(--editorial-line);
    padding-left: 1.2rem;
  }

  .how-heading p,
  .step p,
  .rules p,
  .faq p {
    color: var(--editorial-paper);
    line-height: 1.6;
  }

  .how-heading a {
    color: var(--editorial-ink);
    font-weight: 500;
    text-decoration: underline;
    text-underline-offset: 0.16em;
    text-decoration-color: var(--editorial-copper);
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
    border: 1px solid var(--editorial-line);
    border-radius: 0;
    background: rgb(244 234 215 / 0.045);
    padding: 1.05rem;
  }

  .step::before {
    content: "";
    position: absolute;
    inset: 0 0 auto;
    height: 1px;
    background: linear-gradient(90deg, var(--editorial-copper), transparent);
  }

  .step:nth-child(1) {
    background: linear-gradient(160deg, rgb(176 107 63 / 0.15), rgb(244 234 215 / 0.035) 58%);
  }

  .step:nth-child(2) {
    background: linear-gradient(160deg, rgb(41 55 43 / 0.34), rgb(244 234 215 / 0.035) 58%);
  }

  .step:nth-child(3) {
    background: linear-gradient(160deg, rgb(94 31 32 / 0.24), rgb(244 234 215 / 0.035) 58%);
  }

  .step:nth-child(1)::before {
    background: linear-gradient(90deg, var(--editorial-copper), transparent);
  }

  .step:nth-child(3)::before {
    background: linear-gradient(90deg, var(--editorial-wine), transparent);
  }

  .step-icon {
    width: 2rem;
    height: 2rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    color: var(--editorial-ink);
    background: rgb(244 234 215 / 0.08);
    border: 1px solid var(--editorial-line);
    margin-bottom: 0.9rem;
  }

  .step:nth-child(1) .step-icon {
    color: #fecdd3;
  }

  .step:nth-child(2) .step-icon {
    color: #bfdbfe;
  }

  .step:nth-child(3) .step-icon {
    color: #fde68a;
  }

  .step h3 {
    font-size: 1.05rem;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 400;
    margin-bottom: 0.45rem;
    color: var(--editorial-ink);
  }

  .rules {
    margin-top: 0.85rem;
    border-radius: 0;
    border: 1px solid var(--editorial-line);
    padding: 1rem 1.1rem;
    background:
      linear-gradient(90deg, rgb(176 107 63 / 0.12), transparent),
      rgb(244 234 215 / 0.045);
  }

  .faq {
    margin-top: 1rem;
    display: grid;
    gap: 0.6rem;
  }

  .faq details {
    border: 1px solid var(--editorial-line);
    border-radius: 0;
    background: rgb(244 234 215 / 0.045);
    padding: 0.9rem 1rem;
  }

  .faq details:nth-child(3n + 1) {
    background: rgb(176 107 63 / 0.1);
  }

  .faq details:nth-child(3n + 2) {
    background: rgb(41 55 43 / 0.24);
  }

  .faq details:nth-child(3n + 3) {
    background: rgb(94 31 32 / 0.14);
  }

  .faq details[open] {
    border-color: rgb(244 234 215 / 0.34);
    background: rgb(244 234 215 / 0.08);
  }

  .faq summary {
    cursor: pointer;
    color: var(--editorial-ink);
    font-size: 1rem;
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 400;
    line-height: 1.35;
  }

  .faq summary::marker {
    color: var(--editorial-copper);
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
