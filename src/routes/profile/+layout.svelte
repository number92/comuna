<script>
  import ProfileTabs from '$lib/components/users/ProfileTabs.svelte'
  import { t } from '$lib/translations'
</script>

<svelte:head>
  <title>{$t('profile.profile')}</title>
</svelte:head>

<div class="flex flex-col gap-4 h-full z-0">
  <ProfileTabs />
  <slot />
</div>
