<script lang="ts">
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { infoCircle, pencil, play, pause, phone, check, times, bath } from "svelte-awesome/icons";
  import Footer from "./components/Footer.svelte";

  // binding view
  let text = "";
  let chatting = false;

  let vrc = {
    status: "Not Ready",  // "Ready", "Listening", "Inputting"
    last_status_code: 200,
    result: "",
  };

  class API {
    post(data) {
      console.log("POST", data);
      fetch('/api/spell', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"text": data})
      }).then(res => res.json()).then(res => {
        vrc.last_status_code = res.status;
        if (vrc.last_status_code == 100) {
          vrc.result = `OK: ${res.spell}`;
        } else {
          vrc.result = `Failed: ${data}`;
        }
        chatting = res.chatting;
      });
    }
  }

  class Spell {
    constructor() {
      this.last_data = "";
      this.last_update = new Date();
      this.inputting = false;
      this.chating = false;
      this.table = [];
    }
    clear() {
      if (!text) {
        return;
      }
      this.last_data = text;
      text = "";
      this.last_update = new Date();
      this.inputting = false;
      console.log('cleared', this.last_data, this.last_update);
    }
    post(data) {
      console.log("Spell.post", data);
      if (!data) {
        return;
      }
      if (text !== data) {
        text = data;  // update view
      }
      (new API()).post(data);
      setTimeout(() => {
        this.clear();
      }, 100);
    }
    set_chat(is_chatting) {
      if (is_chatting) {
        this.post('start to chat');
      } else {
        this.post('end to chat');
      }
    }
  }

  class Recognition {
    constructor(lang) {
      let recognition = new webkitSpeechRecognition();
      recognition.interimResults = true;
      recognition.continuous = true;
      if (lang) {
        recognition.lang = vrc.lang;
      }
      recognition.onstart = () => {
        console.log('[Recog] start');
      };
      recognition.onerror = (err) => {
        console.log('[Recog] error:', err);
        setTimeout(() => {
          this.start();
        }, 100);
      };
      recognition.onend = () => {
        console.log('[Recog] end');
      }
      recognition.onresult = (event) => {
        let transcript = event.results[0][0].transcript;
        console.log('[Recog] result:', transcript);
        if (transcript === "") return;
        text = transcript;
      };
      this.recognition = recognition;
      this.ready = false;
      this.listening = false;
    }
    set_lang(lang) {
      this.recognition.lang = lang;
    }
    start() {
      if (!this.ready) return;
      spell.clear();
      if (this.listening) {
        this.recognition.stop();
      }
      setTimeout(() => {
        this.recognition.start();
        this.listening = true;
      }, 100);
    }
    stop() {
      if (!this.ready) return;
      if (!this.listening) return;
      this.recognition.stop();
      this.listening = false;
    }
  }

  function check_chatting() {
    setTimeout(() => {
      spell.set_chat(chatting);
    }, 100);
  }

  let spell = new Spell();
  let recog = new Recognition('en-US');

  function init() {
    fetch('/api/spells').then(res => res.json()).then(data => {
      spell.table = data;
    });
    fetch('/api/lang').then(res => res.json()).then(lang => {
      recog.set_lang(lang);
      recog.ready = true;
      vrc.status = "Ready";
    });
  }

  function watch() {
    // update status
    if (!recog.ready) {
      vrc.status = 'Not Ready';
    } else if (spell.inputting) {
      vrc.status = 'Inputting';
    } else if (recog.listening) {
      vrc.status = 'Listening';
    } else {
      vrc.status = 'Ready';
    }
    console.log(vrc.status);
    // text frozen?
    let elapsed = (new Date()) - spell.last_update;
    if (recog.ready && recog.listening) {
      if (text === "") {
        spell.clear();
      } else if (text === spell.last_data) {
        if (elapsed > 1000) {  // frozen
          spell.post(text);
          setTimeout(() => {
            recog.start();
          }, 100);
        }
      } else {
        spell.inputting = true;
        spell.last_data = text;
        spell.last_update = new Date();
      }
    }
  }

  onMount(() => {
    init();
    setInterval(watch, 250);
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
        <a class="button is-info" on:click={() => recog.start()}>
          <Icon data={play} />
        </a>
        {:else}
        <a class="button is-info" on:click={() => recog.stop()}>
          <Icon data={pause} />
        </a>
        {/if}
      </div>
      <div class="control">
        <form on:submit|preventDefault={() => spell.post(text)}>
          <input class="input"
            class:is-info={vrc.last_status_code == 200}
            class:is-danger={ vrc.last_status_code != 200 }
            type="text" placeholder="Start to speech"
            bind:value={text}
            on:keydown={() => recog.stop()}
          />
        </form>
      </div>
    </div>
    <div>
      <label>
        <input
          type=checkbox
          bind:checked={chatting}
          on:change={check_chatting}
          />
        chat mode
      </label>
    </div>
  </div>
</div>

<div class="section">
  <div class="container">
    <article class="message">
      <div class="message-body">

        <div class="field">
          <!-- Listening/Input Status -->
          <div>
            {#if vrc.status == "Not Ready"}
              <Icon data={times} />
            {:else if vrc.status == "Ready"}
              <Icon data={check} />
            {:else if vrc.status == "Inputting"}
              <Icon data={pencil} />
            {:else if vrc.status == "Listening"}
              <Icon data={phone} />
            {/if}
            {vrc.status}
          </div>
          <!-- Last Spell -->
          {#if spell.last_data}
          <div>
            <Icon data={bath} />
            {spell.last_data}
          </div>
          {/if}
          <!-- Last API Status -->
          {#if vrc.result}
          <div>
            <Icon data={infoCircle} />
            { vrc.result }
          </div>
          {/if}
        </div>

      </div>
    </article>
  </div>
</div>

{#if spell.table}
<div class="section">
  <div class="container">
    <h2 class="subtitle">Spells</h2>
    <div class="content">
      <ul>
      {#each spell.table as s}
        <li>
          <kbd><a on:click={ (event) => { spell.post(event.target.innerText) } }>{s.spell}</a></kbd>
          <code>({s.dest}, {s.args})</code>
        </li>
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
