<script lang="ts">
  export let visible = false
  export let href = '/settings'
</script>

{#if visible}
  <div class="editor-autosave-notice">
    Материал сохранен как черновик, дальнейшее сохранение идет автоматически.
    Все черновики <a href={href}>в профиле</a>.
  </div>
{/if}

<style>
  .editor-autosave-notice {
    border-radius: 0.75rem;
    border: 1px solid rgb(167 243 208);
    background: rgb(236 253 245);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    line-height: 1.5;
    color: rgb(6 78 59);
  }

  .editor-autosave-notice a {
    text-decoration: underline;
    text-decoration-color: rgb(16 185 129 / 0.7);
    text-underline-offset: 2px;
  }

  .editor-autosave-notice a:hover {
    color: rgb(4 120 87);
  }

  :global(.dark) .editor-autosave-notice {
    border-color: rgb(6 78 59 / 0.4);
    background: rgb(6 78 59 / 0.2);
    color: rgb(167 243 208);
  }

  :global(.dark) .editor-autosave-notice a:hover {
    color: rgb(236 253 245);
  }
</style>
