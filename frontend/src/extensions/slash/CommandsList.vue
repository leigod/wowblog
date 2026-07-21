<template>
  <div class="dropdown-menu">
    <div dir="ltr" style="overflow: hidden; position: relative; scrollbar-width: none">
      <div style="overflow: hidden scroll">
        <div style="min-width: 100%; display: table">
          <section id="slash-command-horizontal-menu" class="section-menu">
            <template v-if="items.length">
              <button
                type="button"
                v-for="(nav, navkey) in items"
                :key="navkey"
                :class="{ 'is-selected': navkey === selectedKey }"
                @click="scrollToSection(nav.title)"
              >
                {{ nav.title }}
              </button>
            </template>
          </section>
        </div>
      </div>
    </div>
    <div dir="ltr" style="overflow: hidden; position: relative; scrollbar-width: none">
      <div style="overflow: hidden scroll" class="dropdown-content">
        <div style="min-width: 100%; display: table">
          <template v-if="items.length">
            <section id="slash-command-list-parent" v-for="(section, key) in items" :key="key">
              <div :id="section.title + '-section'" class="section-title">
                {{ section.title }}
              </div>
              <div
                v-for="(item, index) in section.children"
                :key="index"
                @click="selectItem(key, index)"
                :class="{ 'is-selected': key === selectedKey && index === selectedIndex }"
                class="item-container"
              >
                <div class="btn-icon">
                  <IconifyIcon :icon="item.icon" color="#3f3f46" />
                </div>
                <div class="btn-content">
                  <div class="btn-title">{{ item.title }}</div>
                  <div class="btn-description">{{ item.description }}</div>
                </div>
              </div>
            </section>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import IconifyIcon from '@/components/IconIfy.vue'
export default {
  components: {
    IconifyIcon
  },
  props: {
    items: {
      type: Array,
      required: true
    },

    command: {
      type: Function,
      required: true
    }
  },

  data() {
    return {
      selectedKey: 0,
      selectedIndex: 0
    }
  },

  watch: {
    items() {
      this.selectedKey = 0
      this.selectedIndex = 0
    }
  },

  methods: {
    scrollToSection(section) {
      let element = document.getElementById(section + '-section')
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
      }
    },
    onKeyDown({ event }) {
      if (event.key === 'ArrowUp') {
        this.upHandler()
        return true
      }

      if (event.key === 'ArrowDown') {
        this.downHandler()
        return true
      }

      if (event.key === 'Enter') {
        this.enterHandler()
        return true
      }
      return false
    },
    upHandler() {
      if (this.selectedIndex == 0) {
        this.selectedKey = (this.selectedKey + this.items.length - 1) % this.items.length
        this.selectedIndex = this.items[this.selectedKey].children.length - 1
      } else {
        this.selectedIndex =
          (this.selectedIndex + this.items[this.selectedKey].children.length - 1) %
          this.items[this.selectedKey].children.length
      }
      // this.scrollDiv()
    },
    downHandler() {
      if (this.selectedIndex === this.items[this.selectedKey].children.length - 1) {
        this.selectedKey = (this.selectedKey + 1) % this.items.length
        this.selectedIndex = 0
      } else {
        this.selectedIndex = (this.selectedIndex + 1) % this.items[this.selectedKey].children.length
      }
    },
    enterHandler() {
      this.selectItem(this.selectedKey, this.selectedIndex)
    },
    selectItem(key, index) {
      const item = this.items[key].children[index]

      if (item) {
        this.command(item)
      }
    }
  }
}
</script>

<style lang="scss">
/* Dropdown menu */
.dropdown-menu {
  background: var(--white);
  border: 1px solid var(--gray-1);
  border-radius: 0.7rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow: hidden;
  width: 350px;
  padding: 0;

  .section-menu {
    display: flex;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: start;
    justify-content: flex-start;
    gap: 0.5rem;
    border-bottom: 1px solid var(--gray-3);
    background-color: rgb(255 255 255 / 1);
    padding: 0.75rem 1rem;

    button {
      display: flex;
      justify-content: center;
      border-radius: 9999px;
      border-width: 1px;
      background-color: rgb(255 255 255 / 1);
      flex: 1 1 0%;
      padding: 0.25rem 9px;
      font-size: 0.75rem;
      line-height: 1rem;
      color: rgb(82 82 91 / 1);
      border: 1px solid var(--gray-3);
      cursor: pointer;

      &:hover,
      &:hover.is-selected {
        background-color: var(--gray-1);
      }

      &.is-selected {
        background-color: var(--gray-1);
      }
    }
  }

  .dropdown-content {
    width: 100%;
    //height: 100%;
    max-height: 384px;
    & > div {
      display: block;
    }
    scrollbar-width: none;
    -ms-overflow-style: none;
    -webkit-overflow-scrolling: touch;

    section#slash-command-list-parent {
      display: flex;
      height: 100%;
      flex-direction: column;
      gap: 0.5rem;
      background-color: rgb(255 255 255 / 1);
      border-bottom: 1px solid var(--gray-2);
    }
  }

  .section-title {
    display: flex;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
    gap: 0.375rem;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 0.5rem;
    font-size: 0.875rem;
    line-height: 1.25rem;
    font-weight: 400;
    color: rgb(113 113 122 / 1);
  }

  .item-container {
    display: flex;
    width: 100%;
    height: 50px;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    //background-color: rgb(244 244 245 / 1);
    align-items: center;
    cursor: pointer;

    &:hover,
    &:hover.is-selected {
      background-color: var(--gray-1);
    }

    &.is-selected {
      background-color: var(--gray-1);
    }

    .btn-icon {
      position: relative;
      display: flex;
      height: 2.25rem;
      width: 2.25rem;
      align-items: center;
      justify-content: center;
      padding-top: 0.375rem;
      overflow: hidden;
      border-radius: 0.375rem;
      border: 1px solid var(--gray-3);
      background-color: rgb(250 250 250 / 1);
      color: #3f3f46;
    }
    .btn-content {
      display: flex;
      // flex: 1 1 0%;
      flex-direction: column;
      align-items: flex-start;
      text-align: left;
      font-size: 0.875rem;
      line-height: 1.375;
    }
    .btn-title {
      font-weight: 500;
      color: rgb(63 63 70 / 1);
    }
    .btn-description {
      color: rgb(113 113 122 / 1);
    }
  }
}
</style>
