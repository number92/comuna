<script lang="ts">
  import { page } from '$app/stores'
  import { BookOpen, Film, Home, Icon, ListBullet, MapPin } from 'svelte-hero-icons'

  const projects = [
    {
      title: 'Книга интернет сообщества',
      description: 'Общая книга по одному слову',
      href: '/s/book',
      icon: BookOpen,
    },
    {
      title: '365 фильмов',
      description: 'Один фильм в день',
      href: '/s/365-films',
      icon: Film,
    },
    {
      title: 'Имя на карте',
      description: 'Слова из спутниковых снимков',
      href: '/s/landname',
      icon: MapPin,
    },
  ]

  const isActiveProject = (href: string) =>
    $page.url.pathname === href || $page.url.pathname.startsWith(`${href}/`)
</script>

<div class="special-shell">
  <aside class="special-sidebar" aria-label="Спецпроекты">
    <nav class="special-nav">
      <a class="site-link" href="/">
        <span class="nav-icon">
          <Icon src={Home} size="18" mini />
        </span>
        <span>На сайт</span>
      </a>

      <div class="projects-group">
        <div class="group-title">
          <span class="nav-icon">
            <Icon src={ListBullet} size="18" mini />
          </span>
          <span>Все спецпроекты</span>
        </div>

        <div class="project-links">
          {#each projects as project}
            <a
              class:active={isActiveProject(project.href)}
              class="project-link"
              href={project.href}
              aria-current={isActiveProject(project.href) ? 'page' : undefined}
            >
              <span class="project-icon">
                <Icon src={project.icon} size="18" mini />
              </span>
              <span class="project-copy">
                <strong>{project.title}</strong>
                <small>{project.description}</small>
              </span>
            </a>
          {/each}
        </div>
      </div>
    </nav>
  </aside>

  <div class="special-content">
    <slot />
  </div>
</div>

<style>
  .special-shell {
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    min-height: 100vh;
    background: #f8fafc;
    color: #111827;
  }

  .special-sidebar {
    position: sticky;
    top: 80px;
    align-self: start;
    height: calc(100vh - 80px);
    border-right: 1px solid #e5e7eb;
    background: rgba(248, 250, 252, 0.96);
    padding: 18px 14px;
    overflow: auto;
    z-index: 20;
  }

  .special-nav,
  .projects-group,
  .project-links {
    display: grid;
    gap: 10px;
  }

  .site-link,
  .group-title,
  .project-link {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .site-link {
    min-height: 42px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #ffffff;
    color: #111827;
    font-weight: 700;
    padding: 0 12px;
    text-decoration: none;
    transition:
      border-color 160ms ease,
      background 160ms ease;
  }

  .site-link:hover {
    border-color: #cbd5e1;
    background: #f9fafb;
  }

  .projects-group {
    margin-top: 8px;
  }

  .group-title {
    min-height: 34px;
    color: #64748b;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0;
    padding: 0 8px;
    text-transform: uppercase;
  }

  .nav-icon,
  .project-icon {
    display: inline-flex;
    width: 28px;
    height: 28px;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: #f1f5f9;
    color: #334155;
  }

  .project-link {
    min-height: 64px;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #1f2937;
    padding: 10px;
    text-decoration: none;
    transition:
      border-color 160ms ease,
      background 160ms ease,
      color 160ms ease;
  }

  .project-link:hover {
    border-color: #e2e8f0;
    background: #ffffff;
  }

  .project-link.active {
    border-color: #c7d2fe;
    background: #eef2ff;
    color: #1e3a8a;
  }

  .project-link.active .project-icon {
    background: #dbeafe;
    color: #1d4ed8;
  }

  .project-copy {
    display: grid;
    min-width: 0;
    gap: 3px;
  }

  .project-copy strong,
  .project-copy small {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .project-copy strong {
    font-size: 14px;
    line-height: 1.15;
  }

  .project-copy small {
    color: #64748b;
    font-size: 12px;
    line-height: 1.2;
  }

  .special-content {
    min-width: 0;
    background: #ffffff;
  }

  :global(.dark) .special-shell {
    background: #09090b;
    color: #f4f4f5;
  }

  :global(.dark) .special-sidebar {
    border-right-color: #27272a;
    background: rgba(9, 9, 11, 0.96);
  }

  :global(.dark) .special-content {
    background: #09090b;
  }

  :global(.dark) .site-link,
  :global(.dark) .project-link:hover {
    border-color: #27272a;
    background: #18181b;
    color: #f4f4f5;
  }

  :global(.dark) .site-link:hover {
    border-color: #3f3f46;
    background: #1f1f23;
  }

  :global(.dark) .group-title,
  :global(.dark) .project-copy small {
    color: #a1a1aa;
  }

  :global(.dark) .nav-icon,
  :global(.dark) .project-icon {
    background: #27272a;
    color: #d4d4d8;
  }

  :global(.dark) .project-link {
    color: #e4e4e7;
  }

  :global(.dark) .project-link.active {
    border-color: #1d4ed8;
    background: #172554;
    color: #bfdbfe;
  }

  :global(.dark) .project-link.active .project-icon {
    background: #1e3a8a;
    color: #dbeafe;
  }

  @media (max-width: 900px) {
    .special-shell {
      display: block;
    }

    .special-sidebar {
      position: sticky;
      top: 72px;
      height: auto;
      border-right: 0;
      border-bottom: 1px solid #e5e7eb;
      padding: 10px 12px;
    }

    .special-nav {
      gap: 8px;
    }

    .projects-group {
      margin-top: 0;
    }

    .group-title {
      min-height: 28px;
      padding: 0 2px;
    }

    .project-links {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 2px;
    }

    .project-link {
      min-width: 210px;
    }

    .site-link {
      width: max-content;
      min-height: 38px;
    }

    :global(.dark) .special-sidebar {
      border-bottom-color: #27272a;
    }
  }
</style>
