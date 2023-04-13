<script lang="ts">
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { infoCircle } from "svelte-awesome/icons";
  import Footer from "./components/Footer.svelte";

  let status = 200;
  let listening = false;
  let message = "Click Start and Speech";

  let spell = "";
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
      status = data.status;
      if (status == 200) {
        spell = "";
        message = `OK: ${data.spell}`;
      } else {
        message = "Failed";
      }
    });
  }

  let spelltable = [];
  function get_spell_table() {
    fetch('/api/spells').then(res => res.json()).then(data => {
      spelltable = data;
    });
  }

  var SpeechRecognition = webkitSpeechRecognition || SpeechRecognition;
  var recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  // recognition.lang = "ja-JP";
  recognition.interimResults = true;
  // recognition.continuous = true;
  recognition.onsoundstart = () => {
    console.log('[I] Listening...')
  };
  recognition.onnomatch = () => {
    console.log('[I] NoMatch (try again)');
    kick_recognition();
  };
  recognition.onerror = (err) => {
    console.log('[I] Error', err);
    kick_recognition();
  };
  recognition.onsoundend = () => {
    console.log('[I] End');
    post_spell();
    kick_recognition();
  };
  recognition.onresult = (event) => {
    for (var i = event.resultIndex; i < event.results.length; i++){
      if (event.results[i].isFinal){
        spell = event.results[i][0].transcript;
      } else{
        spell = event.results[i][0].transcript;
      }
    }
  };
  function kick_recognition() {
    console.log("kick_recognition");
    if (listening) {
      recognition.stop();
    }
    setTimeout(() => {
      recognition.start();
      listening = true;
    }, 200);
  }
  function stop_recognition() {
    console.log("stop_recognition");
    if (listening) {
      recognition.stop();
    }
    listening = false;
  }

  onMount(() => {
    get_spell_table();
  });
</script>

<svelte:head>
  <title>Spell chanting</title>
</svelte:head>

<div class="section">
  <div class="container">
    <div class="field has-addons">
      <div class="control">
        <form on:submit|preventDefault={post_spell}>
          <input class="input" class:is-info={status == 200} class:is-danger={ status != 200 } type="text" placeholder="spell here" bind:value={spell}>
        </form>
      </div>
      <div class="control">
        <a class="button is-info" on:click={post_spell}>
          Run
        </a>
      </div>
    </div>
    <div class="field has-addons">
      <div class="control">
        <a class="button is-info" on:click={kick_recognition}>
          Start
        </a>
      </div>
      <div class="control">
        <a class="button is-info" on:click={stop_recognition}>
          End
        </a>
      </div>
    </div>
    <div class="field">
      {#if message}
        <div>
          <Icon data={infoCircle} />
          { message }
        </div>
      {/if}
    </div>
  </div>
</div>

{#if spelltable}
<div class="section">
  <div class="container">
    <h2 class="subtitle">Spells</h2>
    <div class="content">
      <ul>
      {#each spelltable as s, i}
        <li><kbd>{s.spell}</kbd> <code>({s.dest}, {s.args})</code></li>
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
