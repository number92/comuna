<div class="editor-route-shell">
  <div class="editor-route-shell__inner">
    <slot />
  </div>
</div>

<style>
  .editor-route-shell {
    width: 100%;
    min-height: 100%;
  }

  .editor-route-shell__inner {
    width: 100%;
    max-width: 72rem;
    margin: 0 auto;
  }

  @media (max-width: 640px) {
    .editor-route-shell__inner {
      max-width: none;
    }
  }
</style>
