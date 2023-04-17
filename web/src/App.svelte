<script lang="ts">
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { infoCircle, pencil, play, pause } from "svelte-awesome/icons";
  import Footer from "./components/Footer.svelte";

  let spell = "";
  let last_spell = "";
  let freezing = 0;
  let vrc = {
    status: "Not Ready",
    last_status_code: 200,
    result: "",
    spelltable: [],
    lang: "en-US",
  };

  var SpeechRecognition = webkitSpeechRecognition || SpeechRecognition;
  var recognition = new SpeechRecognition();
  recognition.lang = vrc.lang;
  recognition.interimResults = true;
  // recognition.continuous = true;

  function init() {
    fetch('/api/spells').then(res => res.json()).then(data => {
      vrc.spelltable = data;
    });
    fetch('/api/lang').then(res => res.json()).then(lang => {
      vrc.lang = lang;
      recognition.lang = lang;
      vrc.status = "Ready";
    });
  }

  function post_spell() {
    if (spell === "") return;
    console.log("POST", spell);
    fetch('/api/spell', {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"text": spell})
    }).then(res => res.json()).then(data => {
      console.log(data);
      vrc.last_status_code = data.status;
      if (vrc.last_status_code == 200) {
        vrc.result = `OK: ${data.spell}`;
      } else {
        vrc.result = `Failed: ${spell}`;
      }
    });
    spell = "";
  }

  function click_spell(event) {
    spell = event.target.innerText;
    post_spell();
  }

  recognition.onsoundstart = () => {
    console.log('[I] Listening...')
  };
  recognition.onnomatch = () => {
    console.log('[I] NoMatch (try again)');
    spell = "";
    kick_recognition();
  };
  recognition.onerror = (err) => {
    console.log('[I] Error', err);
    spell = "";
    kick_recognition();
  };
  recognition.onsoundend = () => {
    console.log('[I] End');
    post_spell();
    kick_recognition();
  };
  recognition.onresult = (event) => {
    let transcript = event.results[0][0].transcript;
    if (transcript === "") return;
    spell = transcript;
    freezing = 0;
    console.log("Recog:", spell);
  };
  function kick_recognition() {
    console.log("kick_recognition");
    freezing = 0;
    try {
      recognition.stop();
    } catch(e) {
    }
    setTimeout(() => {
      try {
        recognition.start();
      } catch(e) {}
      vrc.status = "Now listening...";
    }, 200);
  }
  function stop_recognition() {
    console.log("stop_recognition");
    freezing = 0;
    try {
      vrc.status = "Ready";
      spell = "";
      recognition.stop();
    } catch(e) {}
  }

  function watch_spell() {
    if (vrc.status !== "Now listening...") return;
    if (spell === last_spell) {   // freeze?
      freezing += 1;
    } else {
      freezing = 0;
    }
    console.log("watch", spell, last_spell, freezing);
    if (freezing >= 10) {
      spell == "";
      stop_recognition();
      setTimeout(kick_recognition, 10);
    }
    last_spell = spell;
  }

  onMount(() => {
    init();
    setInterval(watch_spell, 1000);
  });
</script>

<svelte:head>
	<title>VRC/Spell chanting</title>
</svelte:head>

<div class="section">
  <div class="container">
    <div class="field has-addons">
      <div class="control">
        {#if vrc.status == "Not Ready"}
        <a class="button is-info" disabled>
          <Icon data={play} />
        </a>
        {:else if vrc.status == "Ready"}
        <a class="button is-info" on:click={kick_recognition}>
          <Icon data={play} />
        </a>
        {:else}
        <a class="button is-info" on:click={stop_recognition}>
          <Icon data={pause} />
        </a>
        {/if}
      </div>
      <div class="control">
        <form on:submit|preventDefault={post_spell}>
          <input class="input"
            class:is-info={vrc.last_status_code == 200}
            class:is-danger={ vrc.last_status_code != 200 }
            type="text" placeholder="Start to speech" bind:value={spell} />
        </form>
      </div>
    </div>
  </div>
</div>

<div class="section">
  <div class="container">
    <article class="message">
      <div class="message-body">

        <div class="field">
          <div>
            <Icon data={pencil} />
            { vrc.status }
          </div>
        </div>

        {#if vrc.result}
        <div>
          <Icon data={infoCircle} />
          { vrc.result }
        </div>
        {/if}

      </div>
    </article>
  </div>
</div>

{#if vrc.spelltable}
<div class="section">
  <div class="container">
    <h2 class="subtitle">Spells</h2>
    <div class="content">
      <ul>
      {#each vrc.spelltable as s}
        <li><kbd><a on:click={click_spell}>{s.spell}</a></kbd> <code>({s.dest}, {s.args})</code></li>
      {/each}
      </ul>
    </div>
  </div>
</div>
{/if}

<Footer><a href="https://github.com/cympfh/vrc-spell-chanting">cympfh/vrc-spell-chanting</a></Footer>

<style global lang="scss">
  @import "main.scss";
</style>
