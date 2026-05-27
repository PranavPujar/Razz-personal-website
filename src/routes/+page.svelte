<script>
  import Globe from "$lib/Globe.svelte";
  import ImageSlideshow from "$lib/ImageSlideshow.svelte";
  import Streamer from "$lib/Streamer.svelte";
</script>

<svelte:head>
  <title>Rasajna</title>
</svelte:head>

<div class="view-content">
  <Streamer speedDiv={1.9}>
    <ImageSlideshow />
    <div class="bio">
      <p>
        I currently work as a Talent Acquisition Associate at <a
          href="https://www.boehringer-ingelheim.com/"
          target="_blank"
          class="text-link-bi">Boehringer Ingelheim</a
        > in Dubai, supporting recruitment operations across the IMETA region, while
        also pursuing my Master’s in Business Psychology at <a
          href="https://www.hw.ac.uk/dubai"
          target="_blank"
          class="text-link-hw">Heriot-Watt University Dubai</a
        >.
      </p>

      <p>
        Previously, I worked across talent acquisition, HR, and project
        coordination roles in the UAE and remotely, contributing to hiring,
        onboarding, and talent operations for large-scale events including
        COP28, Formula 1 Abu Dhabi, Dubai Run, and Dubai Ride.
      </p>

      <p>
        Alongside industry experience, I actively pursued research in psychology
        and heritage language maintenance among second-generation South Asian
        immigrants in the UAE. My undergraduate research was presented at
        multiple international conferences and later published in IVICOLL 2023.
      </p>

      <p>
        Growing up in India 🇮🇳 and Dubai 🇦🇪 shaped my perspective through a mix
        of South Asian roots and global cultural exposure.
      </p>
    </div>
  </Streamer>

  <Globe />
</div>
