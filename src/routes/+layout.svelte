<script>
  import { onMount } from 'svelte';
  import { beforeNavigate } from '$app/navigation';
  import Nav from '$lib/Nav.svelte';
  import Footer from '$lib/Footer.svelte';
  import SmoothCursor from '$lib/SmoothCursor.svelte';
  import { appReady } from '$lib/stores/app.js';
  import { theme } from '$lib/stores/theme.js';
  import { cancelStream } from '$lib/stream.js';
  import '../app.css';

  let { children } = $props();
  let lenis;

  theme.init();

  beforeNavigate(() => {
    cancelStream();
    if (lenis) lenis.scrollTo(0, { immediate: true });
  });

  onMount(async () => {
    const { default: Lenis } = await import('lenis');

    const timer = setTimeout(() => {
      appReady.set(true);

      // Skip Lenis on touch devices — Lenis v1 intercepts touchmove and calls
      // preventDefault(), which causes scroll to stutter when changing direction.
      // Native touch scroll is already smooth with momentum, so Lenis is only
      // used on pointer:fine devices (mouse/trackpad).
      if (window.matchMedia('(pointer: coarse)').matches) return;

      lenis = new Lenis({
        lerp: 0.09,
        smoothWheel: true,
        wheelMultiplier: 0.9,
        touchMultiplier: 1.4,
      });

      function raf(time) {
        lenis?.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
    }, 100);

    return () => {
      clearTimeout(timer);
      lenis?.destroy();
    };
  });
</script>

<SmoothCursor />
<Nav ready={$appReady} />

<main id="scroll-container" class:ready={$appReady}>
  {@render children()}
  <Footer />
</main>
