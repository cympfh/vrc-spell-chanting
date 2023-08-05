<script lang="ts">
  import { onMount } from "svelte";
  import { writable } from "svelte/store";
  import Icon from "svelte-awesome";
  import { infoCircle, pencil, play, pause, gear } from "svelte-awesome/icons";
  import Footer from "./components/Footer.svelte";

  let vrc = {
    api: {
      last_status_code: 200,
      result: "",
    },
    spell: {
      table: [],
      data: "",
      last_data: "",
      last_updated: new Date(),
      chating: false,
    },
    watch: {
      frozen_time_ms: 1000,
      running: false,
    },
  };

  class Spell {
    constructor() {
    }
    run(data) {
      if (data) {
        this.update(data);
      }
      this.post();
      this.clear();
    }
    update(data) {
      vrc.spell.last_data = vrc.spell.data;
      vrc.spell.data = data;
      vrc.spell.last_updated = new Date();
    }
    clear() {
      vrc.spell.data = "";
      vrc.spell.last_data = "";  // vrc.spell.data;
      vrc.spell.last_updated = new Date();
    }
    // If the input spell is frozen, post it.
    check_frozen() {
      if (!vrc.spell.data) {
        return false;
      }
      if (vrc.spell.last_data === vrc.spell.data) {
        let elapsed = (new Date()) - vrc.spell.last_updated;
        if (elapsed >= vrc.watch.frozen_time_ms) {
          this.run();
          return true;
        }
        return false;
      }
      vrc.spell.last_data = vrc.spell.data;
      vrc.spell.last_updated = new Date();
      return false;
    }
    post() {
      let data = vrc.spell.data;
      if (!data) {
        console.log("cannot POST empty data");
        return;
      }
      console.log("POST", data);
      fetch('/api/spell', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"text": data})
      }).then(res => res.json()).then(data => {
        console.log(data);
        vrc.api.last_status_code = data.status;
        vrc.api.result = `${JSON.stringify(data)}`;
      });
    }
  }

  class Watch {
    constructor(spell) {
      this.spell = spell;
    }
    watch(spell) {
      console.log('watch', vrc.spell.data);
      spell.check_frozen();
    }
    start() {
      spell.clear();
      vrc.watch.running = true;
      let interval = Math.max(100, vrc.watch.frozen_time_ms / 5);
      this.id = setInterval(this.watch, interval, this.spell);
    }
    stop() {
      vrc.watch.running = false;
      clearInterval(this.id);
    }
  }

  function init() {
    fetch('/api/spells').then(res => res.json()).then(data => {
      vrc.spell.table = data;
    });
  }

  let spell = new Spell();
  let watch = new Watch(spell);
  onMount(() => {
    init();
  });
</script>

<svelte:head>
	<title>VRC/Spell chanting</title>
</svelte:head>

<div class="section">
  <div class="container">
    <div class="field has-addons">
      <div class="control">
        {#if !vrc.watch.running}
        <a class="button is-info" on:click={() => { watch.start(); }}>
          <Icon data={play} />
        </a>
        {:else}
        <a class="button is-info" on:click={() => { watch.stop(); }}>
          <Icon data={pause} />
        </a>
        {/if}
      </div>
      <div class="control">
        <form on:submit|preventDefault={() => { spell.run() }}>
          <input class="input"
            class:is-info={vrc.api.last_status_code == 200}
            class:is-danger={vrc.api.last_status_code != 200}
            type="text"
            placeholder="Start to speech (Win+H)"
            bind:value={vrc.spell.data} />
        </form>
      </div>
    </div>
    <div class="field has-addons">
      <details>
        <summary>
          <Icon data={gear} />
          config
        </summary>
        <div class="control">
          <label>
            fronzen time
            <input
              type="range"
              class="slider"
              min=0
              max=4000
              bind:value={vrc.watch.frozen_time_ms} />
            {vrc.watch.frozen_time_ms} (ms)
          </label>
        </div>
      </details>
    </div>
  </div>
</div>

<div class="section">
  <div class="container">
    <article class="message">
      <div class="message-body">

        {#if vrc.api.result}
        <div>
          <Icon data={infoCircle} />
          { vrc.api.result }
        </div>
        {/if}

      </div>
    </article>
  </div>
</div>

{#if vrc.spell.table}
<div class="section">
  <div class="container">
    <h2 class="subtitle">Spells</h2>
    <div class="content">
      <ul>
      {#each vrc.spell.table as s}
        <li><kbd><a on:click={(e) => spell.run(e.target.innerText)}>{s.spell}</a></kbd> <code>({s.dest}, {s.args})</code></li>
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
