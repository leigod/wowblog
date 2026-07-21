<template>
  <div v-if="editor" class="container" :class="customClass">
    <div class="tiptap">
      <div role="toolbar" aria-label="toolbar" data-variant="fixed" class="tiptap-toolbar">
        <div class="tiptap-toolbar-group">
          <el-tooltip>
            <template #content>
              <div>Undo</div>
              <div style="color: silver">⌘+Z</div>
            </template>
            <button @click.prevent="editor.chain().focus().undo().run()"
              :disabled="!editor.can().chain().focus().undo().run()" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('undo') ? 'on' : 'off'" aria-label="Undo" data-disabled="false"
              role="button" tabindex="-1">
              <undo-2-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip>
            <template #content>
              <div>Redo</div>
              <div style="color: silver">⌘+Y</div>
            </template>
            <button @click.prevent="editor.chain().focus().redo().run()"
              :disabled="!editor.can().chain().focus().redo().run()" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('redo') ? 'on' : 'off'">
              <redo-2-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <el-popover placement="bottom" :width="150" trigger="click" :visible="showHeadingPopover">
            <template #reference>
              <button class="tiptap-button" data-style="ghost" :data-active-state="editor.isActive('heading', { level: 1 })
                ? 'on'
                : editor.isActive('heading', { level: 2 })
                  ? 'on'
                  : editor.isActive('heading', { level: 3 })
                    ? 'on'
                    : 'off'
                " @click.prevent="showHeadingPopover = !showHeadingPopover">
                <heading-one-icon v-if="editor.isActive('heading', { level: 1 })" class="tiptap-button-icon" />
                <heading-two-icon v-else-if="editor.isActive('heading', { level: 2 })" class="tiptap-button-icon" />
                <heading-three-icon v-else-if="editor.isActive('heading', { level: 3 })" class="tiptap-button-icon" />
                <heading-icon v-else class="tiptap-button-icon" />
                <el-icon size="8">
                  <ArrowDown />
                </el-icon>
              </button>
            </template>
            <template #default>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
                @click.prevent="setHeading(1)">
                <button :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
                  :data-active-state="editor.isActive('heading', { level: 1 }) ? 'on' : 'off'">
                  <heading-one-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Heading 1</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
                @click.prevent="setHeading(2)">
                <button :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
                  :data-active-state="editor.isActive('heading', { level: 2 }) ? 'on' : 'off'">
                  <heading-two-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Heading 2</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
                @click.prevent="setHeading(3)">
                <button :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
                  :data-active-state="editor.isActive('heading', { level: 3 }) ? 'on' : 'off'">
                  <heading-three-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Heading 3</span>
              </div>
            </template>
          </el-popover>

          <el-tooltip>
            <template #content>
              <div>Bold</div>
              <div style="color: silver">⌘+B</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleBold().run()"
              :disabled="!editor.can().chain().focus().toggleBold().run()" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('bold') ? 'on' : 'off'" aria-label="Bold">
              <bold-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <button @click.prevent="editor.chain().focus().toggleItalic().run()"
            :disabled="!editor.can().chain().focus().toggleItalic().run()"
            :class="{ 'is-active': editor.isActive('italic') }" class="tiptap-button" data-style="ghost"
            :data-active-state="editor.isActive('italic') ? 'on' : 'off'">
            <italic-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().toggleStrike().run()"
            :disabled="!editor.can().chain().focus().toggleStrike().run()"
            :class="{ 'is-active': editor.isActive('strike') }" class="tiptap-button" data-style="ghost"
            :data-active-state="editor.isActive('strike') ? 'on' : 'off'">
            <strike-icon class="tiptap-button-icon" />
          </button>

          <button @click.prevent="editor.chain().focus().toggleUnderline().run()"
            :disabled="!editor.can().chain().focus().toggleUnderline().run()"
            :class="{ 'is-active': editor.isActive('underline') }" class="tiptap-button" data-style="ghost"
            :data-active-state="editor.isActive('underline') ? 'on' : 'off'">
            <underline-icon class="tiptap-button-icon" />
          </button>

          <el-popover placement="bottom" :width="160" trigger="click" :visible="showListPopover">
            <template #reference>
              <button class="tiptap-button" data-style="ghost" :data-active-state="editor.isActive('bulletList') ||
                editor.isActive('orderedList') ||
                editor.isActive('taskList')
                ? 'on'
                : 'off'
                " @click.prevent="showListPopover = !showListPopover">
                <list-ordered-icon v-if="editor.isActive('orderedList')" class="tiptap-button-icon" />
                <list-todo-icon v-else-if="editor.isActive('taskList')" class="tiptap-button-icon" />
                <list-icon v-else class="tiptap-button-icon" />
                <el-icon size="8">
                  <ArrowDown />
                </el-icon>
              </button>
            </template>
            <template #default>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('bulletList') }"
                @click.prevent="toggleList('bullet')">
                <button :class="{ 'is-active': editor.isActive('bulletList') }"
                  :data-active-state="editor.isActive('bulletList') ? 'on' : 'off'">
                  <list-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Bullet list</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('orderedList') }"
                @click.prevent="toggleList('ordered')">
                <button :class="{ 'is-active': editor.isActive('orderedList') }"
                  :data-active-state="editor.isActive('orderedList') ? 'on' : 'off'">
                  <list-ordered-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Ordered list</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive('taskList') }"
                @click.prevent="toggleList('task')">
                <button :class="{ 'is-active': editor.isActive('taskList') }"
                  :data-active-state="editor.isActive('taskList') ? 'on' : 'off'">
                  <list-todo-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Task list</span>
              </div>
            </template>
          </el-popover>
          <el-popover placement="bottom" :width="180" trigger="click" :visible="showTextAlignPopover">
            <template #reference>
              <button class="tiptap-button" data-style="ghost" :data-active-state="editor.isActive({ textAlign: 'left' })
                ? 'on'
                : editor.isActive({ textAlign: 'center' })
                  ? 'on'
                  : editor.isActive({ textAlign: 'right' })
                    ? 'on'
                    : editor.isActive({ textAlign: 'justify' })
                      ? 'on'
                      : 'off'
                " @click.prevent="showTextAlignPopover = !showTextAlignPopover">
                <align-left-icon v-if="editor.isActive({ textAlign: 'left' })" class="tiptap-button-icon" />
                <align-center-icon v-else-if="editor.isActive({ textAlign: 'center' })" class="tiptap-button-icon" />
                <align-right-icon v-else-if="editor.isActive({ textAlign: 'right' })" class="tiptap-button-icon" />
                <align-justify-icon v-else class="tiptap-button-icon" />
                <el-icon size="8">
                  <ArrowDown />
                </el-icon>
              </button>
            </template>
            <template #default>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"
                @click.prevent="setTextAlign('left')">
                <button :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }"
                  :data-active-state="editor.isActive({ textAlign: 'left' }) ? 'on' : 'off'">
                  <align-left-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Align left</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"
                @click.prevent="setTextAlign('center')">
                <button :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }"
                  :data-active-state="editor.isActive({ textAlign: 'center' }) ? 'on' : 'off'">
                  <align-center-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Align center</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"
                @click.prevent="setTextAlign('right')">
                <button :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }"
                  :data-active-state="editor.isActive({ textAlign: 'right' }) ? 'on' : 'off'">
                  <align-right-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Align right</span>
              </div>
              <div class="wy-menu-item" :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }"
                @click.prevent="setTextAlign('justify')">
                <button :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }"
                  :data-active-state="editor.isActive({ textAlign: 'justify' }) ? 'on' : 'off'">
                  <align-justify-icon class="tiptap-button-icon" />
                </button>
                <span class="tiptap-button-text">Align justify</span>
              </div>
            </template>
          </el-popover>
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <el-tooltip content="Highlight">
            <button @click.prevent="editor.chain().focus().toggleHighlight().run()"
              :disabled="!editor.can().chain().focus().toggleHighlight().run()"
              :class="{ 'is-active': editor.isActive('highlight') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('highlight') ? 'on' : 'off'">
              <highlighter-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip content="Link">
            <button @click.prevent="setLink()" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('link') ? 'on' : 'off'">
              <link-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip>
            <template #content>
              <div>Blockquote</div>
              <div style="color: silver">⌘+⇧+B</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleBlockquote().run()"
              :class="{ 'is-active': editor.isActive('blockquote') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('blockquote') ? 'on' : 'off'">
              <block-quote-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip>
            <template #content>
              <div>Code</div>
              <div style="color: silver">⌘+C</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleCode().run()"
              :disabled="!editor.can().chain().focus().toggleCode().run()"
              :class="{ 'is-active': editor.isActive('code') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('code') ? 'on' : 'off'">
              <code-2-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>

          <el-tooltip>
            <template #content>
              <div>Code Block</div>
              <div style="color: silver">⌘+⌥+C</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleCodeBlock().run()"
              :class="{ 'is-active': editor.isActive('codeBlock') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('codeBlock') ? 'on' : 'off'">
              <code-block-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <el-tooltip content="Insert Image">
            <button class="tiptap-button" data-style="ghost" @click.prevent="insertImage">
              <image-plus-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip content="Upload Image">
            <button class="tiptap-button" data-style="ghost" @click.prevent="uploadImage">
              <image-upload-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <el-tooltip>
            <template #content>
              <div>Subscript</div>
              <div style="color: silver">⌘+.</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleSuperscript().run()"
              :class="{ 'is-active': editor.isActive('superscript') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('superscript') ? 'on' : 'off'">
              <superscript-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
          <el-tooltip>
            <template #content>
              <div>Subscript</div>
              <div style="color: silver">⌘+,</div>
            </template>
            <button @click.prevent="editor.chain().focus().toggleSubscript().run()"
              :class="{ 'is-active': editor.isActive('subscript') }" class="tiptap-button" data-style="ghost"
              :data-active-state="editor.isActive('subscript') ? 'on' : 'off'">
              <subscript-icon class="tiptap-button-icon" />
            </button>
          </el-tooltip>
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <button @click.prevent="editor.chain().focus().clearNodes().unsetAllMarks().run()" class="tiptap-button"
            data-style="ghost">
            <clear-style-icon class="tiptap-button-icon" />
          </button>

          <button @click.prevent="editor.chain().focus().setHorizontalRule().run()"
            :class="{ 'is-active': editor.isActive('horizontalRule') }" class="tiptap-button" data-style="ghost"
            :data-active-state="editor.isActive('horizontalRule') ? 'on' : 'off'" data-tooltip="Horizontal line">
            <horizontal-line-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().setHardBreak().run()" class="tiptap-button" data-style="ghost">
            <hardbreak-icon class="tiptap-button-icon" />
          </button>
          <input type="color" @input="handleColorChange" :value="editor?.getAttributes('textStyle').color" />
        </div>
        <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
        <div class="tiptap-toolbar-group">
          <button @click.prevent="
            editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
            " class="tiptap-button" title="Insert table" data-style="ghost"
            :data-active-state="editor.isActive('table') ? 'on' : 'off'">
            <table-insert-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().addColumnAfter().run()" class="tiptap-button"
            title="Add column after" data-style="ghost" aria-label="Add column after" type="button">
            <table-column-insert-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().deleteColumn().run()" class="tiptap-button"
            title="Delete column" data-style="ghost" aria-label="Delete column" type="button">
            <table-column-delete-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().addRowAfter().run()" class="tiptap-button"
            title="Add row after" data-style="ghost" aria-label="Add row after" type="button">
            <table-row-insert-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().deleteRow().run()" class="tiptap-button" title="Delete row"
            data-style="ghost" aria-label="Delete row" type="button">
            <table-row-delete-icon class="tiptap-button-icon" />
          </button>
          <button @click.prevent="editor.chain().focus().deleteTable().run()" class="tiptap-button" title="Delete table"
            data-style="ghost" aria-label="Delete table" type="button">
            <table-delete-icon class="tiptap-button-icon" />
          </button>
        </div>
      </div>
    </div>
    <floating-menu class="floating-menu" :tippy-options="{ duration: 100 }" :editor="editor">
      <button @click.prevent="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }">
        H1
      </button>
      <button @click.prevent="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
        H2
      </button>
      <button @click.prevent="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }">
        H3
      </button>
      <button @click.prevent="editor.chain().focus().toggleBulletList().run()"
        :class="{ 'is-active': editor.isActive('bulletList') }">
        <list-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }" class="tiptap-button"
        :data-active-state="editor.isActive('bold') ? 'on' : 'off'" data-style="ghost">
        <bold-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }" class="tiptap-button"
        :data-active-state="editor.isActive('italic') ? 'on' : 'off'" data-style="ghost">
        <italic-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleStrike().run()"
        :class="{ 'is-active': editor.isActive('strike') }" class="tiptap-button"
        :data-active-state="editor.isActive('strike') ? 'on' : 'off'" data-style="ghost">
        <strike-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleUnderline().run()"
        :class="{ 'is-active': editor.isActive('underline') }" class="tiptap-button"
        :data-active-state="editor.isActive('underline') ? 'on' : 'off'" data-style="ghost">
        <underline-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().setTextAlign('left').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'left' }) ? 'on' : 'off'" data-style="ghost">
        <align-left-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setTextAlign('center').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'center' }) ? 'on' : 'off'" data-style="ghost">
        <align-center-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setTextAlign('right').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'right' }) ? 'on' : 'off'" data-style="ghost">
        <align-right-icon class="tiptap-button-icon" />
      </button>
    </floating-menu>
    <editor-content :editor="editor" class="simple-editor-content" />
  </div>
  <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }" v-if="editor" plugin-key="bubbleMenuOne"
    :should-show="() => {
      if (!editor) return false
      const { from, to } = editor.state.selection
      const text = editor.state.doc.textBetween(from, to)
      return !!text
    }
      ">
    <div class="bubble-menu menu-one">
      <button @click.prevent="editor.chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }" class="tiptap-button"
        :data-active-state="editor.isActive('bold') ? 'on' : 'off'" data-style="ghost">
        <bold-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }" class="tiptap-button"
        :data-active-state="editor.isActive('italic') ? 'on' : 'off'" data-style="ghost">
        <italic-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleStrike().run()"
        :class="{ 'is-active': editor.isActive('strike') }" class="tiptap-button"
        :data-active-state="editor.isActive('strike') ? 'on' : 'off'" data-style="ghost">
        <strike-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleUnderline().run()"
        :class="{ 'is-active': editor.isActive('underline') }" class="tiptap-button"
        :data-active-state="editor.isActive('underline') ? 'on' : 'off'" data-style="ghost">
        <underline-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().setTextAlign('left').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'left' }) ? 'on' : 'off'" data-style="ghost">
        <align-left-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setTextAlign('center').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'center' }) ? 'on' : 'off'" data-style="ghost">
        <align-center-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setTextAlign('right').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'right' }) ? 'on' : 'off'" data-style="ghost">
        <align-right-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().setNode('heading', { level: 1 }).run()" class="tiptap-button"
        :data-active-state="editor.isActive('heading', { level: 1 }) ? 'on' : 'off'" data-style="ghost">
        <heading-one-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setNode('heading', { level: 2 }).run()" class="tiptap-button"
        :data-active-state="editor.isActive('heading', { level: 2 }) ? 'on' : 'off'" data-style="ghost">
        <heading-two-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setNode('heading', { level: 3 }).run()" class="tiptap-button"
        :data-active-state="editor.isActive('heading', { level: 3 }) ? 'on' : 'off'" data-style="ghost">
        <heading-three-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().toggleHighlight().run()" class="tiptap-button"
        :data-active-state="editor.isActive('highlight') ? 'on' : 'off'" data-style="ghost">
        <highlighter-icon class="tiptap-button-icon" />
      </button>
      <input type="color" @input="handleColorChange" :value="editor?.getAttributes('textStyle').color" />
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="setLink" class="tiptap-button" :data-active-state="editor.isActive('link') ? 'on' : 'off'"
        data-style="ghost">
        <link-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().toggleSuperscript().run()"
        :class="{ 'is-active': editor.isActive('superscript') }" class="tiptap-button" data-style="ghost"
        :data-active-state="editor.isActive('superscript') ? 'on' : 'off'">
        <superscript-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().toggleSubscript().run()"
        :class="{ 'is-active': editor.isActive('subscript') }" class="tiptap-button" data-style="ghost"
        :data-active-state="editor.isActive('subscript') ? 'on' : 'off'">
        <subscript-icon class="tiptap-button-icon" />
      </button>
    </div>
  </bubble-menu>
  <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }" v-if="editor" plugin-key="bubbleMenuTwo"
    :should-show="() => {
      return editor?.isActive('highlight') ?? false
    }
      ">
    <div class="bubble-menu menu-two">
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#eeeeee' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#eeeeee' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight" style="--highlight-color: var(--tt-color-highlight-gray)"></span>
      </button>
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#dcfce7' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#dcfce7' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight" style="--highlight-color: var(--tt-color-highlight-green)"></span>
      </button>
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#e0f2fe' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#e0f2fe' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight" style="--highlight-color: var(--tt-color-highlight-blue)"></span>
      </button>
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#f3e8ff' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#f3e8ff' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight" style="--highlight-color: var(--tt-color-highlight-purple)"></span>
      </button>
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#ffe4e6' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#ffe4e6' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight" style="--highlight-color: var(--tt-color-highlight-red)"></span>
      </button>
      <button @click.prevent="editor.chain().focus().toggleHighlight({ color: '#fbe604' }).run()"
        :data-active-state="editor.isActive('highlight', { color: '#fbe604' }) ? 'on' : 'off'" class="tiptap-button"
        data-style="ghost">
        <span class="tiptap-button-highlight"
          style="--highlight-color: var(--tt-color-highlight-yellow-contrast)"></span>
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().unsetHighlight().run()"
        :data-active-state="editor.isActive('highlight') ? 'on' : 'off'" class="tiptap-button" data-style="ghost">
        <ban-icon class="tiptap-button-icon" />
      </button>
    </div>
  </bubble-menu>
  <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }" v-if="editor" plugin-key="bubbleMenuThree"
    :should-show="() => {
      return editor?.isActive('image') ?? false
    }
      ">
    <div class="bubble-menu menu-three">
      <button @click.prevent="insertImage" :data-active-state="editor.isActive('image') ? 'on' : 'off'"
        class="tiptap-button" data-style="ghost">
        <!-- <IconIfy icon="lucide:edit-3" class="tiptap-button-icon" /> -->
        <el-icon class="tiptap-button-icon">
          <EditPen />
        </el-icon>
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="editor.chain().focus().setTextAlign('left').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'left' }) ? 'on' : 'off'" data-style="ghost">
        <align-left-icon class="tiptap-button-icon" />
      </button>

      <button @click.prevent="editor.chain().focus().setTextAlign('center').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'center' }) ? 'on' : 'off'" data-style="ghost">
        <align-center-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setTextAlign('right').run()" class="tiptap-button"
        :data-active-state="editor.isActive('textAlign', { align: 'right' }) ? 'on' : 'off'" data-style="ghost">
        <align-right-icon class="tiptap-button-icon" />
      </button>
      <div class="tiptap-separator" data-orientation="vertical" role="none"></div>
      <button @click.prevent="setLink()" class="tiptap-button"
        :data-active-state="editor.isActive('link') ? 'on' : 'off'" data-style="ghost">
        <link-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().setImage({ src: '' }).run()" class="tiptap-button"
        data-style="ghost">
        <trash-icon class="tiptap-button-icon" />
      </button>
    </div>
  </bubble-menu>
  <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }" v-if="editor" plugin-key="bubbleMenuFour"
    :should-show="() => {
      return editor?.isActive('link') ?? false
    }
      ">
    <div class="bubble-menu menu-four">
      <button @click.prevent="openLink()" class="tiptap-button" data-style="ghost">
        <IconIfy icon="lucide:external-link" class="tiptap-button-icon" />
      </button>
      <button @click.prevent="setLink()" class="tiptap-button" data-style="ghost">
        <link-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().unsetLink().run()" class="tiptap-button" data-style="ghost">
        <trash-icon class="tiptap-button-icon" />
      </button>
    </div>
  </bubble-menu>
  <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }" v-if="editor" plugin-key="bubbleMenuFive"
    :should-show="() => {
      return editor?.isActive('table') ?? false
    }
      ">
    <div class="bubble-menu menu-five">
      <button @click.prevent="editor.chain().focus().addColumnAfter().run()" class="tiptap-button"
        title="Add column after" data-style="ghost" aria-label="Add column after" type="button">
        <table-column-insert-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().deleteColumn().run()" class="tiptap-button" title="Delete column"
        data-style="ghost" aria-label="Delete column" type="button">
        <table-column-delete-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().addRowAfter().run()" class="tiptap-button" title="Add row after"
        data-style="ghost" aria-label="Add row after" type="button">
        <table-row-insert-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().deleteRow().run()" class="tiptap-button" title="Delete row"
        data-style="ghost" aria-label="Delete row" type="button">
        <table-row-delete-icon class="tiptap-button-icon" />
      </button>
      <button @click.prevent="editor.chain().focus().deleteTable().run()" class="tiptap-button" title="Delete table"
        data-style="ghost" aria-label="Delete table" type="button">
        <table-delete-icon class="tiptap-button-icon" />
      </button>
    </div>
  </bubble-menu>

  <el-dialog v-model="dialogLinkFormVisible" title="添加链接" :width="dialogWidth">
    <el-form :model="linkForm" :label-position="labelPosition">
      <el-form-item label="Url" :label-width="formLabelWidth">
        <el-input v-model="linkForm.url" autocomplete="off" placeholder="https://example.com" />
      </el-form-item>
      <el-form-item label="" :label-width="formLabelWidth">
        <el-checkbox v-model="linkForm.openwindow" label="在新窗口中打开" size="large" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click.prevent="dialogLinkFormVisible = false">取消</el-button>
        <el-button type="primary" @click.prevent="onSubmitLinkForm"> 确认 </el-button>
      </div>
    </template>
  </el-dialog>
  <el-dialog v-model="dialogInsertImageFormVisible" title="从URL添加图片" :width="dialogWidth">
    <el-form :model="insertImageForm" :label-position="labelPosition">
      <el-form-item label="Url" :label-width="formLabelWidth">
        <el-input v-model="insertImageForm.url" autocomplete="off" placeholder="https://example.com/image.jpg" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click.prevent="dialogInsertImageFormVisible = false">取消</el-button>
        <el-button type="primary" @click.prevent="onSubmitInsertImageForm"> 确认 </el-button>
      </div>
    </template>
  </el-dialog>
  <el-dialog v-model="dialogUploadImageFormVisible" title="上传图片" :width="uploadDialogWidth">
    <el-upload class="upload-demo" drag :auto-upload="false" :on-change="handleFileChange" :show-file-list="false"
      accept="image/jpeg,image/jpg,image/png,image/gif">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">Drop file here or <em>click to upload</em></div>
      <template #tip>
        <div class="el-upload__tip">Supports JPG, PNG, GIF files with size less than 2MB</div>
      </template>
    </el-upload>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onBeforeUnmount, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { Color } from '@tiptap/extension-color'
import ListItem from '@tiptap/extension-list-item'
import TextStyle from '@tiptap/extension-text-style'
import { TextAlignImage } from '../extensions/text-align-image'
import StarterKit from '@tiptap/starter-kit'
import { ImageAligned } from '../extensions/image-aligned'
import Underline from '@tiptap/extension-underline'
import Highlight from '@tiptap/extension-highlight'
import Link from '@tiptap/extension-link'
import Superscript from '@tiptap/extension-superscript'
import Subscript from '@tiptap/extension-subscript'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Table from '@tiptap/extension-table'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TableRow from '@tiptap/extension-table-row'
import Mention from '@tiptap/extension-mention'
import { BubbleMenu, EditorContent, FloatingMenu, useEditor } from '@tiptap/vue-3'

import suggestion from '../extensions/mention/suggestion'

// @ts-ignore - highlight.js sub-module imports
import css from 'highlight.js/lib/languages/css'
// @ts-ignore - highlight.js sub-module imports
import js from 'highlight.js/lib/languages/javascript'
// @ts-ignore - highlight.js sub-module imports
import html from 'highlight.js/lib/languages/xml'
// @ts-ignore - highlight.js sub-module imports
import ts from 'highlight.js/lib/languages/typescript'

import { all, createLowlight } from 'lowlight'

// import BoldIcon from './tiptap-icons/bold-icon.vue'
// import ItalicIcon from './tiptap-icons/italic-icon.vue'
// import StrikeIcon from './tiptap-icons/strike-icon.vue'
// import CodeBlockIcon from './tiptap-icons/code-block-icon.vue'
// import BlockQuoteIcon from './tiptap-icons/block-quote-icon.vue'
// import Undo2Icon from './tiptap-icons/undo2-icon.vue'
// import Redo2Icon from './tiptap-icons/redo2-icon.vue'
// import Code2Icon from './tiptap-icons/code2-icon.vue'
// import ListOrderedIcon from './tiptap-icons/list-ordered-icon.vue'
// import ListIcon from './tiptap-icons/list-icon.vue'
// import UnderlineIcon from './tiptap-icons/underline-icon.vue'
// import HighlighterIcon from './tiptap-icons/highlighter-icon.vue'
// import AlignCenterIcon from './tiptap-icons/align-center-icon.vue'
// import AlignJustifyIcon from './tiptap-icons/align-justify-icon.vue'
// import AlignLeftIcon from './tiptap-icons/align-left-icon.vue'
// import AlignRightIcon from './tiptap-icons/align-right-icon.vue'
// import LinkIcon from './tiptap-icons/link-icon.vue'
// import SubscriptIcon from './tiptap-icons/subscript-icon.vue'
// import SuperscriptIcon from './tiptap-icons/superscript-icon.vue'
// import ListTodoIcon from './tiptap-icons/list-todo-icon.vue'
// import ClearStyleIcon from './tiptap-icons/clear-style-icon.vue'
// import HorizontalLineIcon from './tiptap-icons/horizontal-line-icon.vue'
// import TableInsertIcon from './tiptap-icons/table-insert-icon.vue'
// import TableDeleteIcon from './tiptap-icons/table-delete-icon.vue'
// import TableRowInsertIcon from './tiptap-icons/table-row-insert-icon.vue'
// import TableRowDeleteIcon from './tiptap-icons/table-row-delete-icon.vue'
// import TableColumnInsertIcon from './tiptap-icons/table-column-insert-icon.vue'
// import TableColumnDeleteIcon from './tiptap-icons/table-column-delete-icon.vue'
// import HardbreakIcon from './tiptap-icons/hardbreak-icon.vue'
// import ColorIcon from './tiptap-icons/color-icon.vue'
// import HeadingIcon from './tiptap-icons/heading-icon.vue'
// import HeadingOneIcon from './tiptap-icons/heading-one-icon.vue'
// import HeadingTwoIcon from './tiptap-icons/heading-two-icon.vue'
// import HeadingThreeIcon from './tiptap-icons/heading-three-icon.vue'
// import BanIcon from './tiptap-icons/ban-icon.vue'
// import ImageUploadIcon from './tiptap-icons/image-upload-icon.vue'
// import ImagePlusIcon from './tiptap-icons/image-plus-icon.vue'

// Props 定义
interface Props {
  modelValue?: string
  placeholder?: string
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: 'Write something...',
  customClass: ''
})

// Emits 定义
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// 移动端检测
const isMobile = ref(false)
const windowWidth = ref(window.innerWidth)

const checkMobile = () => {
  windowWidth.value = window.innerWidth
  isMobile.value = windowWidth.value < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 响应式对话框宽度和表单标签位置
const dialogWidth = computed(() => isMobile.value ? '90%' : '500px')
const uploadDialogWidth = computed(() => isMobile.value ? '90%' : '700px')
const formLabelWidth = computed(() => isMobile.value ? '80px' : '50px')
const labelPosition = computed(() => isMobile.value ? 'top' : 'right')

// 响应式状态
const dialogLinkFormVisible = ref(false)
const dialogInsertImageFormVisible = ref(false)
const dialogUploadImageFormVisible = ref(false)
const showHeadingPopover = ref(false)
const showTextAlignPopover = ref(false)
const showListPopover = ref(false)

const linkForm = reactive({
  url: '',
  openwindow: false
})

const insertImageForm = reactive({
  url: ''
})

// 创建 lowlight 实例
const lowlight = createLowlight(all)
lowlight.register('html', html)
lowlight.register('css', css)
lowlight.register('js', js)
lowlight.register('ts', ts)

// Tiptap 编辑器初始化
const editor = useEditor({
  content: props.modelValue,
  editorProps: {
    attributes: {
      class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none'
    }
  },
  extensions: [
    ImageAligned,
    Color.configure({
      types: [TextStyle.name, ListItem.name]
    }),
    TextStyle.configure(),
    StarterKit.configure({
      codeBlock: false
    }),
    Underline,
    Highlight.configure({
      multicolor: true
    }),
    TextAlignImage,
    Link.configure({
      openOnClick: false,
      defaultProtocol: 'https'
    }),
    Superscript,
    Subscript,
    CodeBlockLowlight.configure({
      lowlight
    }),
    TaskList,
    TaskItem.configure({
      nested: true
    }),
    Table.configure({
      resizable: true
    }),
    TableRow,
    TableHeader,
    TableCell,
    Mention.configure({
      HTMLAttributes: {
        class: 'mention'
      },
      renderText({ options, node }) {
        return `${options.suggestion.char}${node.attrs.label ?? node.attrs.id}`
      },
      suggestion
    })
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  onFocus() {
    // 关闭所有弹出菜单
    showHeadingPopover.value = false
    showTextAlignPopover.value = false
    showListPopover.value = false
  }
})

// 监听 modelValue 变化
watch(
  () => props.modelValue,
  (newVal) => {
    if (editor.value && newVal !== editor.value.getHTML()) {
      editor.value.commands.setContent(newVal)
    }
  }
)

// 方法
const setLink = () => {
  if (!editor.value) return
  const previousUrl = editor.value.getAttributes('link').href
  linkForm.url = previousUrl || ''
  dialogLinkFormVisible.value = true
}

// 在新标签页打开当前选中的链接（仅在 bubble menu 已激活 link 时触发）
const openLink = () => {
  if (!editor.value) return
  const href = editor.value.getAttributes('link').href
  if (href) {
    window.open(href, '_blank', 'noopener,noreferrer')
  }
}

const setHeading = (level: 1 | 2 | 3 | 4 | 5 | 6) => {
  if (!editor.value) return
  editor.value.chain().focus().toggleHeading({ level }).run()
  showHeadingPopover.value = false
}

const setTextAlign = (align: 'left' | 'center' | 'right' | 'justify') => {
  if (!editor.value) return
  editor.value.chain().focus().setTextAlign(align).run()
  showTextAlignPopover.value = false
}

const toggleList = (type: 'bullet' | 'ordered' | 'task') => {
  if (!editor.value) return

  switch (type) {
    case 'bullet':
      editor.value.chain().focus().toggleBulletList().run()
      break
    case 'ordered':
      editor.value.chain().focus().toggleOrderedList().run()
      break
    case 'task':
      editor.value.chain().focus().toggleTaskList().run()
      break
  }
  showListPopover.value = false
}

const onSubmitLinkForm = () => {
  if (!editor.value) return

  dialogLinkFormVisible.value = false

  if (linkForm.url === null || linkForm.url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }

  if (linkForm.openwindow) {
    editor.value
      .chain()
      .focus()
      .extendMarkRange('link')
      .setLink({ href: linkForm.url, target: '_blank' })
      .run()
  } else {
    editor.value
      .chain()
      .focus()
      .extendMarkRange('link')
      .setLink({ href: linkForm.url })
      .run()
  }
}

const insertImage = () => {
  insertImageForm.url = ''
  dialogInsertImageFormVisible.value = true
}

const onSubmitInsertImageForm = () => {
  if (!editor.value) return

  dialogInsertImageFormVisible.value = false

  if (insertImageForm.url === null || insertImageForm.url === '') {
    return
  }

  editor.value.chain().focus().setImage({ src: insertImageForm.url }).run()
}

const uploadImage = () => {
  dialogUploadImageFormVisible.value = true
}

// 处理文件选择 - 转换为 base64 并插入到编辑器
const handleFileChange = (file: any) => {
  const rawFile = file.raw

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(rawFile.type)) {
    ElMessage.error('You can only upload JPG, PNG, GIF files!')
    return
  }

  // 验证文件大小
  if (rawFile.size / 1024 / 1024 > 5) {
    ElMessage.error('File size exceeds 5MB limit!')
    return
  }

  // 转换为 base64
  const reader = new FileReader()
  reader.onload = (e) => {
    const base64Url = e.target?.result as string
    if (editor.value) {
      editor.value.chain().focus().setImage({ src: base64Url }).run()
    }
    dialogUploadImageFormVisible.value = false
    ElMessage.success('Image uploaded successfully!')
  }
  reader.onerror = () => {
    ElMessage.error('Failed to read image file!')
  }
  reader.readAsDataURL(rawFile)
}

const handleColorChange = (event: Event) => {
  if (!editor.value) return
  const target = event.target as HTMLInputElement
  if (target.value) {
    editor.value.chain().focus().setColor(target.value).run()
  }
}

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style lang="scss">
:root {
  --tt-toolbar-height: 2.75rem;
  --tt-safe-area-bottom: env(safe-area-inset-bottom, 0px);
  --tt-toolbar-bg-color: var(--white);
  --tt-toolbar-border-color: var(--tt-gray-light-a-100);
}

html {
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    Segoe UI,
    Roboto,
    Helvetica Neue,
    Arial,
    Noto Sans,
    sans-serif,
    'Apple Color Emoji',
    'Segoe UI Emoji',
    Segoe UI Symbol,
    'Noto Color Emoji';
  line-height: 1.5;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
}

body {
  --tt-toolbar-height: 44px;
  --tt-theme-text: var(--tt-gray-light-900);
}

.dark body {
  --tt-theme-text: var(--tt-gray-dark-900);
}

body {
  font-family: Inter, sans-serif;
  color: var(--tt-theme-text);
  font-optical-sizing: auto;
  font-weight: 400;
  font-style: normal;
  padding: 0;
}

/* Basic editor styles */
.tiptap {
  caret-color: var(--purple);
  // margin: 1.5rem;
}

.tiptap {
  :first-child {
    margin-top: 0;
  }

  /* List styles */
  // ul,
  // ol {
  //   padding: 0 1rem;
  //   margin: 1.25rem 1rem 1.25rem 0.4rem;

  //   li p {
  //     margin-top: 0.25em;
  //     margin-bottom: 0.25em;
  //   }
  // }

  /* Heading styles */
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    line-height: 1.1;
    margin-top: 2.5rem;
    text-wrap: pretty;
  }

  h1,
  h2 {
    margin-top: 3.5rem;
    margin-bottom: 1.5rem;
  }

  h1 {
    font-size: 1.4rem;
  }

  h2 {
    font-size: 1.2rem;
  }

  h3 {
    font-size: 1.1rem;
  }

  h4,
  h5,
  h6 {
    font-size: 1rem;
  }

  a {
    color: var(--purple);
    cursor: pointer;

    &:hover {
      color: var(--purple-contrast);
    }
  }

  img {
    display: block;
    height: auto;
    margin: 1.5rem 0;
    max-width: 100%;

    &.ProseMirror-selectednode {
      outline: 3px solid var(--purple);
    }
  }

  // 基于父元素 text-align 样式控制图片对齐
  p[style*="text-align: left"],
  h1[style*="text-align: left"],
  h2[style*="text-align: left"],
  h3[style*="text-align: left"],
  .text-align-left {
    text-align: left;

    img {
      margin-left: 0;
      margin-right: auto;
    }
  }

  p[style*="text-align: center"],
  h1[style*="text-align: center"],
  h2[style*="text-align: center"],
  h3[style*="text-align: center"],
  .text-align-center {
    text-align: center;

    img {
      margin-left: auto;
      margin-right: auto;
    }
  }

  p[style*="text-align: right"],
  h1[style*="text-align: right"],
  h2[style*="text-align: right"],
  h3[style*="text-align: right"],
  .text-align-right {
    text-align: right;

    img {
      margin-left: auto;
      margin-right: 0;
    }
  }

  table {
    border-collapse: collapse;
    margin: 0;
    overflow: hidden;
    table-layout: fixed;
    width: 100%;

    td,
    th {
      border: 1px solid var(--gray-3);
      box-sizing: border-box;
      min-width: 1em;
      padding: 6px 8px;
      position: relative;
      vertical-align: top;

      >* {
        margin-bottom: 0;
      }
    }

    th {
      background-color: var(--gray-1);
      font-weight: bold;
      text-align: left;
    }

    .selectedCell:after {
      background: var(--gray-2);
      content: '';
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      pointer-events: none;
      position: absolute;
      z-index: 2;
    }

    .column-resize-handle {
      background-color: var(--purple);
      bottom: -2px;
      pointer-events: none;
      position: absolute;
      right: -2px;
      top: 0;
      width: 4px;
    }
  }

  .tableWrapper {
    margin: 1.5rem 0;
    overflow-x: auto;
  }

  &.resize-cursor {
    cursor: ew-resize;
    cursor: col-resize;
  }

  /* Code and preformatted text styles */
  code {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    color: var(--black);
    font-size: 0.85rem;
    padding: 1.5em 2em;
    border: 1px solid var(--gray-3);
    display: block;
  }

  pre {
    background: var(--black);
    border-radius: 0.5rem;
    color: var(--white);
    font-family: 'JetBrainsMono', monospace;
    margin: 1.5rem 0;
    padding: 0.75rem 1rem;

    code {
      background: none;
      color: inherit;
      font-size: 0.8rem;
      padding: 0;
    }

    /* Code styling */
    .hljs-comment,
    .hljs-quote {
      color: #616161;
    }

    .hljs-variable,
    .hljs-template-variable,
    .hljs-attribute,
    .hljs-tag,
    .hljs-name,
    .hljs-regexp,
    .hljs-link,
    .hljs-name,
    .hljs-selector-id,
    .hljs-selector-class {
      color: #f98181;
    }

    .hljs-number,
    .hljs-meta,
    .hljs-built_in,
    .hljs-builtin-name,
    .hljs-literal,
    .hljs-type,
    .hljs-params {
      color: #fbbc88;
    }

    .hljs-string,
    .hljs-symbol,
    .hljs-bullet {
      color: #b9f18d;
    }

    .hljs-title,
    .hljs-section {
      color: #faf594;
    }

    .hljs-keyword,
    .hljs-selector-tag {
      color: #70cff8;
    }

    .hljs-emphasis {
      font-style: italic;
    }

    .hljs-strong {
      font-weight: 700;
    }
  }

  blockquote {
    border-left: 3px solid var(--tt-gray-light-a-200);
    /**--gray-3 */
    margin: 1.5rem 0;
    padding-left: 1rem;
  }

  hr {
    border: none;
    border-top: 1px solid var(--tt-gray-light-a-100);
    /**--gray-2 */
    margin: 2rem 0;
  }

  .mention {
    background-color: var(--purple-light);
    border-radius: 0.4rem;
    box-decoration-break: clone;
    color: var(--purple);
    padding: 0.1rem 0.3rem;
  }

  input[type='color' i] {
    appearance: auto;
    inline-size: 24px;
    block-size: 24px;
    cursor: default;
    //box-sizing: border-box;
    background-color: transparent;
    color: buttontext;
    // border-width: 1px;
    // border-style: solid;
    // border-color: buttonborder;
    // border-image: initial;
    border: transparent;
    padding: 1px 2px;
    width: 24px;
    height: 24px;
  }

  input[type='color' i]:hover {
    background-color: var(--gray-3);
    border-radius: 4px;
    border-color: var(--gray-3);
    border-width: 1px;
    border-style: solid;
  }

  /* Toolbar styles */
  .dark {
    --tt-toolbar-bg-color: var(--black);
    --tt-toolbar-border-color: var(--tt-gray-dark-a-50);
  }

  .tiptap-toolbar {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .tiptap-toolbar-group {
    display: flex;
    align-items: center;
    gap: 0.125rem;
  }

  .tiptap-separator+.tiptap-toolbar-group:empty,
  .tiptap-toolbar-group:empty,
  .tiptap-toolbar-group:empty+.tiptap-separator {
    display: none;
  }

  .tiptap-toolbar[data-variant='fixed'] {
    position: -webkit-sticky;
    position: sticky;
    top: 0;
    z-index: 10;
    width: 100%;
    min-height: var(--tt-toolbar-height);
    background: var(--tt-toolbar-bg-color);
    border-bottom: 1px solid var(--tt-toolbar-border-color);
    padding: 0 0.5rem;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .tiptap-toolbar[data-variant='fixed']::-webkit-scrollbar {
    display: none;
  }

  @media (max-width: 768px) {
    .tiptap-toolbar[data-variant='fixed'] {
      position: fixed;
      top: auto;
      bottom: 0;
      min-height: calc(var(--tt-toolbar-height) + var(--tt-safe-area-bottom));
      height: auto;
      max-height: calc(var(--tt-toolbar-height) * 3 + var(--tt-safe-area-bottom) + 1rem);
      border-top: 1px solid var(--tt-toolbar-border-color);
      border-bottom: none;
      padding: 0.5rem 0.5rem calc(var(--tt-safe-area-bottom) + 0.5rem);
      flex-wrap: wrap;
      justify-content: flex-start;
      align-content: flex-start;
      z-index: 100;
      overflow-y: auto;
      overflow-x: hidden;
    }

    .tiptap-toolbar[data-variant='fixed'] .tiptap-toolbar-group {
      flex: 0 0 auto;
    }

    .tiptap-toolbar[data-variant='fixed'] .tiptap-separator {
      display: none;
    }
  }

  .tiptap-toolbar[data-variant='floating'] {
    --tt-toolbar-padding: 0.125rem;
    --tt-toolbar-border-width: 1px;
    padding: 0.188rem;
    border-radius: calc(var(--tt-toolbar-padding) + var(--tt-radius-lg) + var(--tt-toolbar-border-width));
    border: var(--tt-toolbar-border-width) solid var(--tt-toolbar-border-color);
    background-color: var(--tt-toolbar-bg-color);
    box-shadow: var(--tt-shadow-elevated-md);
    outline: none;
    overflow: hidden;
  }

  .tiptap-toolbar[data-variant='floating'][data-plain='true'] {
    padding: 0;
    border-radius: 0;
    border: none;
    box-shadow: none;
    background-color: rgba(0, 0, 0, 0);
  }

  @media screen and (max-width: 768px) {
    .tiptap-toolbar[data-variant='floating'] {
      width: 100%;
      border-radius: 0;
      border: none;
      box-shadow: none;
    }
  }

  .tiptap-tooltip {
    --tt-tooltip-bg: var(--tt-gray-light-900);
    --tt-tooltip-text: var(--white);
    --tt-kbd: var(--tt-gray-dark-a-400);
  }

  .dark .tiptap-tooltip {
    --tt-tooltip-bg: var(--white);
    --tt-tooltip-text: var(--tt-gray-light-600);
    --tt-kbd: var(--tt-gray-light-a-400);
  }

  .tiptap-tooltip {
    z-index: 200;
    overflow: hidden;
    border-radius: var(--tt-radius-md, 0.375rem);
    background-color: var(--tt-tooltip-bg);
    padding: 0.375rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--tt-tooltip-text);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  .tiptap-tooltip kbd {
    display: inline-block;
    text-align: center;
    vertical-align: baseline;
    font-family:
      ui-sans-serif,
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      Segoe UI,
      Roboto,
      Helvetica Neue,
      Arial,
      Noto Sans,
      sans-serif;
    text-transform: capitalize;
    color: var(--tt-kbd);
  }

  .tiptap-separator {
    --tt-link-border-color: var(--tt-gray-light-a-200);
  }

  .dark .tiptap-separator {
    --tt-link-border-color: var(--tt-gray-dark-a-200);
  }

  .tiptap-separator {
    flex-shrink: 0;
    background-color: var(--tt-link-border-color);
  }

  .tiptap-separator[data-orientation='horizontal'] {
    height: 1px;
    width: 100%;
  }

  .tiptap-separator[data-orientation='vertical'] {
    height: 1.5rem;
    width: 1px;
  }

  .tiptap-button {
    --tt-button-default-bg-color: var(--tt-gray-light-a-100);
    --tt-button-hover-bg-color: var(--tt-gray-light-200);
    --tt-button-active-bg-color: var(--tt-gray-light-a-200);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-100);
    --tt-button-active-bg-color-subdued: var(--tt-gray-light-a-200);
    --tt-button-active-hover-bg-color: var(--tt-gray-light-300);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-200);
    --tt-button-active-hover-bg-color-subdued: var(--tt-gray-light-a-300);
    --tt-button-disabled-bg-color: var(--tt-gray-light-a-50);
    --tt-button-default-text-color: var(--tt-gray-light-a-600);
    --tt-button-hover-text-color: var(--tt-gray-light-a-900);
    --tt-button-active-text-color: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-light-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-color: var(--tt-gray-light-a-600);
    --tt-button-hover-icon-color: var(--tt-gray-light-a-900);
    --tt-button-active-icon-color: var(--tt-brand-color-500);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-600);
    --tt-button-active-icon-color-subdued: var(--tt-gray-light-a-900);
    --tt-button-disabled-icon-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-sub-color: var(--tt-gray-light-a-400);
    --tt-button-hover-icon-sub-color: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color: var(--tt-gray-light-a-400);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-light-a-400);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-light-a-100);
    --tt-button-default-dropdown-arrows-color: var(--tt-gray-light-a-600);
    --tt-button-hover-dropdown-arrows-color: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-light-a-600);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-light-a-600);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-light-a-400);
  }

  .dark .tiptap-button {
    --tt-button-default-bg-color: var(--tt-gray-dark-a-100);
    --tt-button-hover-bg-color: var(--tt-gray-dark-200);
    --tt-button-active-bg-color: var(--tt-gray-dark-a-200);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-900);
    --tt-button-active-bg-color-subdued: var(--tt-gray-dark-a-200);
    --tt-button-active-hover-bg-color: var(--tt-gray-dark-300);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-800);
    --tt-button-active-hover-bg-color-subdued: var(--tt-gray-dark-a-300);
    --tt-button-disabled-bg-color: var(--tt-gray-dark-a-50);
    --tt-button-default-text-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-text-color: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-dark-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-dark-a-300);
    --tt-button-default-icon-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-icon-color: var(--tt-gray-dark-a-900);
    --tt-button-active-icon-color: var(--tt-brand-color-400);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-400);
    --tt-button-active-icon-color-subdued: var(--tt-gray-dark-a-900);
    --tt-button-disabled-icon-color: var(--tt-gray-dark-a-400);
    --tt-button-default-icon-sub-color: var(--tt-gray-dark-a-300);
    --tt-button-hover-icon-sub-color: var(--tt-gray-dark-a-400);
    --tt-button-active-icon-sub-color: var(--tt-gray-dark-a-300);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-dark-a-400);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-dark-a-300);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-dark-a-100);
    --tt-button-default-dropdown-arrows-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-dropdown-arrows-color: var(--tt-gray-dark-a-700);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-dark-a-600);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-dark-a-700);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-dark-a-600);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-dark-a-400);
  }

  .tiptap-button[data-style='ghost'] {
    --tt-button-default-bg-color: var(--transparent);
    --tt-button-hover-bg-color: var(--tt-gray-light-200);
    --tt-button-active-bg-color: var(--tt-gray-light-a-100);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-100);
    --tt-button-active-bg-color-subdued: var(--tt-gray-light-a-100);
    --tt-button-active-hover-bg-color: var(--tt-gray-light-200);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-200);
    --tt-button-active-hover-bg-color-subdued: var(--tt-gray-light-a-200);
    --tt-button-disabled-bg-color: var(--transparent);
    --tt-button-default-text-color: var(--tt-gray-light-a-600);
    --tt-button-hover-text-color: var(--tt-gray-light-a-900);
    --tt-button-active-text-color: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-light-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-color: var(--tt-gray-light-a-600);
    --tt-button-hover-icon-color: var(--tt-gray-light-a-900);
    --tt-button-active-icon-color: var(--tt-brand-color-500);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-600);
    --tt-button-active-icon-color-subdued: var(--tt-gray-light-a-900);
    --tt-button-disabled-icon-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-sub-color: var(--tt-gray-light-a-400);
    --tt-button-hover-icon-sub-color: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color: var(--tt-gray-light-a-400);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-light-a-400);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-light-a-100);
    --tt-button-default-dropdown-arrows-color: var(--tt-gray-light-a-600);
    --tt-button-hover-dropdown-arrows-color: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-light-a-600);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-light-a-600);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-light-a-400);
  }

  .dark .tiptap-button[data-style='ghost'] {
    --tt-button-default-bg-color: var(--transparent);
    --tt-button-hover-bg-color: var(--tt-gray-dark-200);
    --tt-button-active-bg-color: var(--tt-gray-dark-a-100);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-900);
    --tt-button-active-bg-color-subdued: var(--tt-gray-dark-a-100);
    --tt-button-active-hover-bg-color: var(--tt-gray-dark-200);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-800);
    --tt-button-active-hover-bg-color-subdued: var(--tt-gray-dark-a-200);
    --tt-button-disabled-bg-color: var(--transparent);
    --tt-button-default-text-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-text-color: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-dark-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-dark-a-300);
    --tt-button-default-icon-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-icon-color: var(--tt-gray-dark-a-900);
    --tt-button-active-icon-color: var(--tt-brand-color-400);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-300);
    --tt-button-active-icon-color-subdued: var(--tt-gray-dark-a-900);
    --tt-button-disabled-icon-color: var(--tt-gray-dark-a-400);
    --tt-button-default-icon-sub-color: var(--tt-gray-dark-a-300);
    --tt-button-hover-icon-sub-color: var(--tt-gray-dark-a-400);
    --tt-button-active-icon-sub-color: var(--tt-gray-dark-a-300);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-dark-a-400);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-dark-a-300);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-dark-a-100);
    --tt-button-default-dropdown-arrows-color: var(--tt-gray-dark-a-600);
    --tt-button-hover-dropdown-arrows-color: var(--tt-gray-dark-a-700);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-dark-a-600);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-dark-a-700);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-dark-a-600);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-dark-a-400);
  }

  .tiptap-button[data-style='primary'] {
    --tt-button-default-bg-color: var(--tt-brand-color-500);
    --tt-button-hover-bg-color: var(--tt-brand-color-600);
    --tt-button-active-bg-color: var(--tt-brand-color-100);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-100);
    --tt-button-active-bg-color-subdued: var(--tt-brand-color-100);
    --tt-button-active-hover-bg-color: var(--tt-brand-color-200);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-200);
    --tt-button-active-hover-bg-color-subdued: var(--tt-brand-color-200);
    --tt-button-disabled-bg-color: var(--tt-gray-light-a-100);
    --tt-button-default-text-color: var(--white);
    --tt-button-hover-text-color: var(--white);
    --tt-button-active-text-color: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-light-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-light-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-color: var(--white);
    --tt-button-hover-icon-color: var(--white);
    --tt-button-active-icon-color: var(--tt-brand-color-600);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-600);
    --tt-button-active-icon-color-subdued: var(--tt-brand-color-600);
    --tt-button-disabled-icon-color: var(--tt-gray-light-a-400);
    --tt-button-default-icon-sub-color: var(--tt-gray-dark-a-500);
    --tt-button-hover-icon-sub-color: var(--tt-gray-dark-a-500);
    --tt-button-active-icon-sub-color: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-light-a-500);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-light-a-500);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-light-a-100);
    --tt-button-default-dropdown-arrows-color: var(--white);
    --tt-button-hover-dropdown-arrows-color: var(--white);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-light-a-700);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-light-a-700);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-light-a-400);
  }

  .dark .tiptap-button[data-style='primary'] {
    --tt-button-default-bg-color: var(--tt-brand-color-500);
    --tt-button-hover-bg-color: var(--tt-brand-color-600);
    --tt-button-active-bg-color: var(--tt-brand-color-900);
    --tt-button-active-bg-color-emphasized: var(--tt-brand-color-900);
    --tt-button-active-bg-color-subdued: var(--tt-brand-color-900);
    --tt-button-active-hover-bg-color: var(--tt-brand-color-800);
    --tt-button-active-hover-bg-color-emphasized: var(--tt-brand-color-800);
    --tt-button-active-hover-bg-color-subdued: var(--tt-brand-color-800);
    --tt-button-disabled-bg-color: var(--tt-gray-dark-a-100);
    --tt-button-default-text-color: var(--white);
    --tt-button-hover-text-color: var(--white);
    --tt-button-active-text-color: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-emphasized: var(--tt-gray-dark-a-900);
    --tt-button-active-text-color-subdued: var(--tt-gray-dark-a-900);
    --tt-button-disabled-text-color: var(--tt-gray-dark-a-300);
    --tt-button-default-icon-color: var(--white);
    --tt-button-hover-icon-color: var(--white);
    --tt-button-active-icon-color: var(--tt-brand-color-400);
    --tt-button-active-icon-color-emphasized: var(--tt-brand-color-400);
    --tt-button-active-icon-color-subdued: var(--tt-brand-color-400);
    --tt-button-disabled-icon-color: var(--tt-gray-dark-a-300);
    --tt-button-default-icon-sub-color: var(--tt-gray-dark-a-400);
    --tt-button-hover-icon-sub-color: var(--tt-gray-dark-a-500);
    --tt-button-active-icon-sub-color: var(--tt-gray-dark-a-300);
    --tt-button-active-icon-sub-color-emphasized: var(--tt-gray-dark-a-400);
    --tt-button-active-icon-sub-color-subdued: var(--tt-gray-dark-a-300);
    --tt-button-disabled-icon-sub-color: var(--tt-gray-dark-a-100);
    --tt-button-default-dropdown-arrows-color: var(--white);
    --tt-button-hover-dropdown-arrows-color: var(--white);
    --tt-button-active-dropdown-arrows-color: var(--tt-gray-dark-a-600);
    --tt-button-active-dropdown-arrows-color-emphasized: var(--tt-gray-dark-a-600);
    --tt-button-active-dropdown-arrows-color-subdued: var(--tt-gray-dark-a-600);
    --tt-button-disabled-dropdown-arrows-color: var(--tt-gray-dark-a-400);
  }

  .tiptap-button-group {
    align-items: center;
    display: flex;
    gap: 0.125rem;
  }

  .tiptap-button-group,
  .tiptap-button-group [data-orientation='vertical'],
  .tiptap-button-group[data-orientation='vertical'] {
    flex-direction: column;
  }

  .tiptap-button-group [data-orientation='horizontal'],
  .tiptap-button-group[data-orientation='horizontal'] {
    flex-direction: row;
  }

  .tiptap-button {
    font-size: 0.875rem;
    font-weight: 500;
    font-feature-settings:
      'salt' on,
      'cv01' on;
    line-height: 1.15;
    height: 2rem;
    min-width: 2rem;
    border: none;
    padding: 0.5rem;
    gap: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--tt-radius-lg, 0.75rem);
    transition-property: background, color, opacity;
    transition-duration: var(--tt-transition-duration-default);
    transition-timing-function: var(--tt-transition-easing-default);
  }

  .tiptap-button:focus-visible {
    outline: none;
  }

  .tiptap-button[data-focus-visible='true'],
  .tiptap-button[data-highlighted='true'] {
    background-color: var(--tt-button-hover-bg-color);
    color: var(--tt-button-hover-text-color);
  }

  .tiptap-button[data-size='large'] {
    font-size: 0.9375rem;
    height: 2.375rem;
    min-width: 2.375rem;
    padding: 0.625rem;
  }

  .tiptap-button[data-size='small'] {
    font-size: 0.75rem;
    line-height: 1.2;
    height: 1.5rem;
    min-width: 1.5rem;
    padding: 0.3125rem;
    border-radius: var(--tt-radius-md, 0.5rem);
  }

  .tiptap-button .tiptap-button-text {
    padding: 0 0.125rem;
    flex-grow: 1;
    text-align: left;
    line-height: 1.5rem;
  }

  .tiptap-button[data-text-trim='on'] .tiptap-button-text {
    text-overflow: ellipsis;
    overflow: hidden;
  }

  .tiptap-button .tiptap-button-dropdown-arrows,
  .tiptap-button .tiptap-button-dropdown-small,
  .tiptap-button .tiptap-button-icon,
  .tiptap-button .tiptap-button-icon-sub {
    pointer-events: none;
    flex-shrink: 0;
  }

  .tiptap-button .tiptap-button-icon {
    width: 1rem;
    height: 1rem;
  }

  .tiptap-button[data-size='large'] .tiptap-button-icon {
    width: 1.125rem;
    height: 1.125rem;
  }

  .tiptap-button[data-size='small'] .tiptap-button-icon {
    width: 0.875rem;
    height: 0.875rem;
  }

  .tiptap-button .tiptap-button-icon-sub {
    width: 1rem;
    height: 1rem;
  }

  .tiptap-button[data-size='large'] .tiptap-button-icon-sub {
    width: 1.125rem;
    height: 1.125rem;
  }

  .tiptap-button[data-size='small'] .tiptap-button-icon-sub {
    width: 0.875rem;
    height: 0.875rem;
  }

  .tiptap-button .tiptap-button-dropdown-arrows {
    width: 0.75rem;
    height: 0.75rem;
  }

  .tiptap-button[data-size='large'] .tiptap-button-dropdown-arrows {
    width: 0.875rem;
    height: 0.875rem;
  }

  .tiptap-button .tiptap-button-dropdown-small,
  .tiptap-button[data-size='small'] .tiptap-button-dropdown-arrows {
    width: 0.625rem;
    height: 0.625rem;
  }

  .tiptap-button[data-size='large'] .tiptap-button-dropdown-small {
    width: 0.75rem;
    height: 0.75rem;
  }

  .tiptap-button[data-size='small'] .tiptap-button-dropdown-small {
    width: 0.5rem;
    height: 0.5rem;
  }

  .tiptap-button:has(> svg):not(:has(> :not(svg))) {
    gap: 0.125rem;
  }

  .tiptap-button:has(> svg):not(:has(> :not(svg)))[data-size='large'],
  .tiptap-button:has(> svg):not(:has(> :not(svg)))[data-size='small'] {
    gap: 0.125rem;
  }

  .tiptap-button:has(> svg:nth-of-type(2)):has(> .tiptap-button-dropdown-small):not( :has(> svg:nth-of-type(3))):not(:has(> .tiptap-button-text)) {
    gap: 0;
    padding-right: 0.25rem;
  }

  .tiptap-button:has(> svg:nth-of-type(2)):has(> .tiptap-button-dropdown-small):not( :has(> svg:nth-of-type(3))):not(:has(> .tiptap-button-text))[data-size='large'] {
    padding-right: 0.375rem;
  }

  .tiptap-button:has(> svg:nth-of-type(2)):has(> .tiptap-button-dropdown-small):not( :has(> svg:nth-of-type(3))):not(:has(> .tiptap-button-text))[data-size='small'] {
    padding-right: 0.25rem;
  }

  .tiptap-button .tiptap-button-emoji {
    width: 1rem;
    display: flex;
    justify-content: center;
  }

  .tiptap-button[data-size='large'] .tiptap-button-emoji {
    width: 1.125rem;
  }

  .tiptap-button[data-size='small'] .tiptap-button-emoji {
    width: 0.875rem;
  }

  .tiptap-button {
    background-color: var(--tt-button-default-bg-color);
    color: var(--tt-button-default-text-color);
  }

  .tiptap-button .tiptap-button-icon {
    color: var(--tt-button-default-icon-color);
  }

  .tiptap-button .tiptap-button-icon-sub {
    color: var(--tt-button-default-icon-sub-color);
  }

  .tiptap-button .tiptap-button-dropdown-arrows,
  .tiptap-button .tiptap-button-dropdown-small {
    color: var(--tt-button-default-dropdown-arrows-color);
  }

  .tiptap-button:hover,
  .tiptap-button[data-active-item='true']:not([disabled]) {
    background-color: var(--tt-button-hover-bg-color);
    color: var(--tt-button-hover-text-color);
  }

  .tiptap-button:hover .tiptap-button-icon,
  .tiptap-button[data-active-item='true']:not([disabled]) .tiptap-button-icon {
    color: var(--tt-button-hover-icon-color);
  }

  .tiptap-button:hover .tiptap-button-icon-sub,
  .tiptap-button[data-active-item='true']:not([disabled]) .tiptap-button-icon-sub {
    color: var(--tt-button-hover-icon-sub-color);
  }

  .tiptap-button:hover .tiptap-button-dropdown-arrows,
  .tiptap-button:hover .tiptap-button-dropdown-small,
  .tiptap-button[data-active-item='true']:not([disabled]) .tiptap-button-dropdown-arrows,
  .tiptap-button[data-active-item='true']:not([disabled]) .tiptap-button-dropdown-small {
    color: var(--tt-button-hover-dropdown-arrows-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled]),
  .tiptap-button[data-state='open']:not([disabled]) {
    background-color: var(--tt-button-active-bg-color);
    color: var(--tt-button-active-text-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled]) .tiptap-button-icon,
  .tiptap-button[data-state='open']:not([disabled]) .tiptap-button-icon {
    color: var(--tt-button-active-icon-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled]) .tiptap-button-icon-sub,
  .tiptap-button[data-state='open']:not([disabled]) .tiptap-button-icon-sub {
    color: var(--tt-button-active-icon-sub-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled]) .tiptap-button-dropdown-arrows,
  .tiptap-button[data-active-state='on']:not([disabled]) .tiptap-button-dropdown-small,
  .tiptap-button[data-state='open']:not([disabled]) .tiptap-button-dropdown-arrows,
  .tiptap-button[data-state='open']:not([disabled]) .tiptap-button-dropdown-small {
    color: var(--tt-button-active-dropdown-arrows-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled]):hover,
  .tiptap-button[data-state='open']:not([disabled]):hover {
    background-color: var(--tt-button-active-hover-bg-color);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized'],
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized'] {
    background-color: var(--tt-button-active-bg-color-emphasized);
    color: var(--tt-button-active-text-color-emphasized);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized'] .tiptap-button-icon,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized'] .tiptap-button-icon {
    color: var(--tt-button-active-icon-color-emphasized);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized'] .tiptap-button-icon-sub,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized'] .tiptap-button-icon-sub {
    color: var(--tt-button-active-icon-sub-color-emphasized);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized'] .tiptap-button-dropdown-arrows,
  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized'] .tiptap-button-dropdown-small,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized'] .tiptap-button-dropdown-arrows,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized'] .tiptap-button-dropdown-small {
    color: var(--tt-button-active-dropdown-arrows-color-emphasized);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='emphasized']:hover,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='emphasized']:hover {
    background-color: var(--tt-button-active-hover-bg-color-emphasized);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued'],
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued'] {
    background-color: var(--tt-button-active-bg-color-subdued);
    color: var(--tt-button-active-text-color-subdued);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued'] .tiptap-button-icon,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued'] .tiptap-button-icon {
    color: var(--tt-button-active-icon-color-subdued);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued'] .tiptap-button-icon-sub,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued'] .tiptap-button-icon-sub {
    color: var(--tt-button-active-icon-sub-color-subdued);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued'] .tiptap-button-dropdown-arrows,
  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued'] .tiptap-button-dropdown-small,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued'] .tiptap-button-dropdown-arrows,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued'] .tiptap-button-dropdown-small {
    color: var(--tt-button-active-dropdown-arrows-color-subdued);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued']:hover,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued']:hover {
    background-color: var(--tt-button-active-hover-bg-color-subdued);
  }

  .tiptap-button[data-active-state='on']:not([disabled])[data-appearance='subdued']:hover .tiptap-button-icon,
  .tiptap-button[data-state='open']:not([disabled])[data-appearance='subdued']:hover .tiptap-button-icon {
    color: var(--tt-button-active-icon-color-subdued);
  }

  .tiptap-button:disabled {
    background-color: var(--tt-button-disabled-bg-color);
    color: var(--tt-button-disabled-text-color);
  }

  .tiptap-button:disabled .tiptap-button-icon {
    color: var(--tt-button-disabled-icon-color);
  }
}

/** simple editor */
.simple-editor-content {
  .tiptap.ProseMirror {
    padding: 0;
  }
}

.tiptap.ProseMirror {
  font-family:
    DM Sans,
    sans-serif;
  white-space: pre-wrap;
  outline: none;
  caret-color: var(--tt-cursor-color);
}

.tiptap.ProseMirror {
  --tt-checklist-bg-color: var(--tt-gray-light-a-100);
  --tt-checklist-bg-active-color: var(--tt-gray-light-a-900);
  --tt-checklist-border-color: var(--tt-gray-light-a-200);
  --tt-checklist-border-active-color: var(--tt-gray-light-a-900);
  --tt-checklist-check-icon-color: var(--white);
  --tt-checklist-text-active: var(--tt-gray-light-a-500);
  --tt-inline-code-bg-color: var(--tt-gray-light-a-100);
  --tt-inline-code-text-color: var(--tt-gray-light-a-700);
  --tt-inline-code-border-color: var(--tt-gray-light-a-200);
  --tt-codeblock-bg: var(--tt-gray-light-a-50);
  --tt-codeblock-text: var(--tt-gray-light-a-800);
  --tt-codeblock-border: var(--tt-gray-light-a-200);
  --blockquote-bg-color: var(--tt-gray-light-900);
  --link-text-color: var(--tt-brand-color-500);
  --separator-color: var(--tt-gray-light-a-200);
  --thread-text: var(--tt-gray-light-900);
  --placeholder-color: var(--tt-gray-light-a-400);
  --tiptap-mathematics-bg-color: var(--tt-gray-light-a-200);
  --tiptap-mathematics-border-color: var(--tt-brand-color-500);
}

.dark .tiptap.ProseMirror {
  --tt-checklist-bg-color: var(--tt-gray-dark-a-100);
  --tt-checklist-bg-active-color: var(--tt-gray-dark-a-900);
  --tt-checklist-border-color: var(--tt-gray-dark-a-200);
  --tt-checklist-border-active-color: var(--tt-gray-dark-a-900);
  --tt-checklist-check-icon-color: var(--black);
  --tt-checklist-text-active: var(--tt-gray-dark-a-500);
  --tt-inline-code-bg-color: var(--tt-gray-dark-a-100);
  --tt-inline-code-text-color: var(--tt-gray-dark-a-700);
  --tt-inline-code-border-color: var(--tt-gray-dark-a-200);
  --tt-codeblock-bg: var(--tt-gray-dark-a-50);
  --tt-codeblock-text: var(--tt-gray-dark-a-800);
  --tt-codeblock-border: var(--tt-gray-dark-a-200) --blockquote-bg-color: var(--tt-gray-dark-900);
  --link-text-color: var(--tt-brand-color-400);
  --separator-color: var(--tt-gray-dark-a-200);
  --thread-text: var(--tt-gray-dark-900);
  --placeholder-color: var(--tt-gray-dark-a-400);
  --tiptap-mathematics-bg-color: var(--tt-gray-dark-a-200);
  --tiptap-mathematics-border-color: var(--tt-brand-color-400);
}

.tiptap.ProseMirror ol,
.tiptap.ProseMirror ul {
  margin-top: 1.5em;
  margin-bottom: 1.5em;
  padding-left: 1.5em;
}

.tiptap.ProseMirror ol:first-child,
.tiptap.ProseMirror ul:first-child {
  margin-top: 0;
}

.tiptap.ProseMirror ol:last-child,
.tiptap.ProseMirror ul:last-child {
  margin-bottom: 0;
}

.tiptap.ProseMirror ol ol,
.tiptap.ProseMirror ol ul,
.tiptap.ProseMirror ul ol,
.tiptap.ProseMirror ul ul {
  margin-top: 0;
  margin-bottom: 0;
}

.tiptap.ProseMirror li p {
  margin-top: 0;
}

.tiptap.ProseMirror ol {
  list-style: decimal;
}

.tiptap.ProseMirror ol ol {
  list-style: lower-alpha;
}

.tiptap.ProseMirror ol ol ol {
  list-style: lower-roman;
}

.tiptap.ProseMirror ul:not([data-type='taskList']) {
  list-style: disc;
}

.tiptap.ProseMirror ul:not([data-type='taskList']) ul {
  list-style: circle;
}

.tiptap.ProseMirror ul:not([data-type='taskList']) ul ul {
  list-style: disc;
}

.tiptap.ProseMirror ul[data-type='taskList'] {
  padding-left: 0.25em;
}

.tiptap.ProseMirror ul[data-type='taskList'] li {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.tiptap.ProseMirror ul[data-type='taskList'] li:not(:has(> p:first-child)) {
  list-style-type: none;
}

.tiptap.ProseMirror ul[data-type='taskList'] li[data-checked='true']>div>p {
  opacity: 0.5;
  text-decoration: line-through;
}

.tiptap.ProseMirror ul[data-type='taskList'] li[data-checked='true']>div>p span {
  text-decoration: line-through;
}

.tiptap.ProseMirror ul[data-type='taskList'] li label {
  position: relative;
  padding-top: 4px;
  padding-right: 8px;
}

.tiptap.ProseMirror ul[data-type='taskList'] li label input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.tiptap.ProseMirror ul[data-type='taskList'] li label span {
  display: block;
  width: 1em;
  height: 1em;
  border: 1px solid var(--tt-checklist-border-color);
  border-radius: var(--tt-radius-xs, 0.25rem);
  position: relative;
  cursor: pointer;
  background-color: var(--tt-checklist-bg-color);
  transition:
    background-color 80ms ease-out,
    border-color 80ms ease-out;
}

.tiptap.ProseMirror ul[data-type='taskList'] li label span:before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 0.75em;
  height: 0.75em;
  background-color: var(--tt-checklist-check-icon-color);
  opacity: 0;
  -webkit-mask: url('data:image/svg+xml,%3Csvg%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22currentColor%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20fill-rule%3D%22evenodd%22%20clip-rule%3D%22evenodd%22%20d%3D%22M21.4142%204.58579C22.1953%205.36683%2022.1953%206.63317%2021.4142%207.41421L10.4142%2018.4142C9.63317%2019.1953%208.36684%2019.1953%207.58579%2018.4142L2.58579%2013.4142C1.80474%2012.6332%201.80474%2011.3668%202.58579%2010.5858C3.36683%209.80474%204.63317%209.80474%205.41421%2010.5858L9%2014.1716L18.5858%204.58579C19.3668%203.80474%2020.6332%203.80474%2021.4142%204.58579Z%22%20fill%3D%22currentColor%22%2F%3E%3C%2Fsvg%3E') center/contain no-repeat;
  mask: url('data:image/svg+xml,%3Csvg%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22currentColor%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20fill-rule%3D%22evenodd%22%20clip-rule%3D%22evenodd%22%20d%3D%22M21.4142%204.58579C22.1953%205.36683%2022.1953%206.63317%2021.4142%207.41421L10.4142%2018.4142C9.63317%2019.1953%208.36684%2019.1953%207.58579%2018.4142L2.58579%2013.4142C1.80474%2012.6332%201.80474%2011.3668%202.58579%2010.5858C3.36683%209.80474%204.63317%209.80474%205.41421%2010.5858L9%2014.1716L18.5858%204.58579C19.3668%203.80474%2020.6332%203.80474%2021.4142%204.58579Z%22%20fill%3D%22currentColor%22%2F%3E%3C%2Fsvg%3E') center/contain no-repeat;
}

.tiptap.ProseMirror ul[data-type='taskList'] li label input[type='checkbox']:checked+span {
  background: var(--tt-checklist-bg-active-color);
  border-color: var(--tt-checklist-border-active-color);
}

.tiptap.ProseMirror ul[data-type='taskList'] li label input[type='checkbox']:checked+span:before {
  opacity: 1;
}

.tiptap.ProseMirror ul[data-type='taskList'] li div {
  flex: 1 1;
  min-width: 0;
}

@media screen and (max-width: 768px) {
  .simple-editor-content .tiptap.ProseMirror {
    padding: 1rem 1.5rem;
  }

  .simple-editor-content .tiptap.ProseMirror p {
    font-size: 16px;
    line-height: 1.6;
  }

  .simple-editor-content .tiptap.ProseMirror h1,
  .simple-editor-content .tiptap.ProseMirror h2,
  .simple-editor-content .tiptap.ProseMirror h3 {
    margin-top: 2rem;
    margin-bottom: 1rem;
  }

  .simple-editor-content .tiptap.ProseMirror h1 {
    font-size: 1.5rem;
  }

  .simple-editor-content .tiptap.ProseMirror h2 {
    font-size: 1.25rem;
  }

  .simple-editor-content .tiptap.ProseMirror h3 {
    font-size: 1.1rem;
  }
}

@media screen and (max-width: 480px) {
  .simple-editor-content .tiptap.ProseMirror {
    padding: 0.75rem 1rem;
  }
}

/* Bubble menu */
.tippy-box {
  max-width: fit-content !important;
}

.bubble-menu,
.floating-menu {
  background-color: var(--tt-toolbar-bg-color);
  border: 1px solid var(--gray-3);
  border-radius: var(--tt-radius-lg);
  box-shadow: var(--tt-shadow-elevated-md);
  display: flex;
  padding: 0.2rem;
  gap: 0.2rem;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-start;

  button svg {
    width: 1rem;
    height: 1rem;
  }

  input {
    height: 1.5rem;
    width: 1.5rem;
    border: transparent;
    background-color: unset;

    &:hover {
      background-color: var(--gray-3);
      color: var(--purple);
      border-radius: var(--tt-radius-lg);
      height: 2rem;
      width: 2rem;
      padding: 0.3rem 0.35rem;
    }
  }

  button {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: unset;
    color: var(--black);
    border: transparent;
    padding: 0.5rem;
    margin: 0;
    border-radius: var(--tt-radius-lg);
    width: 2rem;
    height: 2rem;

    &:hover {
      background-color: var(--gray-3);
      color: var(--purple);
    }

    &.is-active {
      background-color: var(--gray-3);
      color: var(--purple);

      &:hover {
        background-color: var(--purple-contrast);
        color: var(--white);
      }
    }
  }

  /* 高亮颜色按钮特殊处理 */
  .tiptap-button-highlight {
    position: relative;
    display: block;
    width: 1.25rem;
    height: 1.25rem;
    margin: 0 -0.175rem;
    border-radius: var(--tt-radius-xl);
    background-color: var(--highlight-color);
    transition: transform 0.2s ease;
  }

  .tiptap-button-highlight:after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    left: 0;
    top: 0;
    border-radius: inherit;
    box-sizing: border-box;
    border: 1px solid var(--highlight-color);
    filter: brightness(95%);
    mix-blend-mode: multiply;
  }

  .dark .tiptap-button-highlight:after {
    filter: brightness(140%);
    mix-blend-mode: lighten;
  }

  .tiptap-button[data-active-state='on'] .tiptap-button-highlight:after {
    filter: brightness(80%);
  }

  .dark .tiptap-button[data-active-state='on'] .tiptap-button-highlight:after {
    filter: brightness(180%);
  }
}


.tiptap-button-highlight {
  position: relative;
  display: block;
  width: 1.25rem;
  height: 1.25rem;
  margin: 0 -0.175rem;
  border-radius: var(--tt-radius-xl);
  background-color: var(--highlight-color);
  transition: transform 0.2s ease;
}

.tiptap-button-highlight:after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  border-radius: inherit;
  box-sizing: border-box;
  border: 1px solid var(--highlight-color);
  filter: brightness(95%);
  mix-blend-mode: multiply;
}

.dark .tiptap-button-highlight:after {
  filter: brightness(140%);
  mix-blend-mode: lighten;
}

.tiptap-button[data-active-state='on'] .tiptap-button-highlight:after {
  filter: brightness(80%);
}

.dark .tiptap-button[data-active-state='on'] .tiptap-button-highlight:after {
  filter: brightness(180%);
}

.wy-menu-item {
  padding: 0.25rem;
  display: flex;
  align-items: center;
  //gap: 0.5rem;
  cursor: default;
  border-radius: 0.5rem;

  button {
    background-color: unset;
    //padding: 0.275rem 0.425rem;
    margin-right: 0.5rem;
    border-radius: 0.3rem;
    border: 0;
    width: 2rem;
    height: 2rem;

    svg {
      width: 95%;
      height: 95%;
    }

    &.is-active {
      background-color: var(--white);
      color: var(--purple);

      &:hover {
        color: var(--purple-contrast);
      }
    }
  }

  &:hover {
    background-color: var(--gray-3);
    font-weight: 800;
  }

  &.is-active {
    background-color: var(--white);
    color: var(--purple);
    font-weight: 800;

    &:hover {
      color: var(--purple-contrast);
    }
  }
}

/* 移动端适配 */
@media screen and (max-width: 768px) {

  /* 对话框样式优化 */
  .el-dialog {
    margin: 5vh auto;
    max-height: 90vh;
    overflow: auto;
  }

  .el-dialog__body {
    padding: 15px;
  }

  /* 上传区域优化 */
  .upload-demo {
    width: 100%;
  }

  .el-upload-dragger {
    width: 100%;
    height: 150px;
  }

  /* 表单优化 */
  .el-form-item {
    margin-bottom: 15px;
  }

  .el-input__inner {
    font-size: 16px;
    /* 防止 iOS 自动缩放 */
  }

  /* 工具栏按钮组优化 */
  .tiptap-toolbar-group {
    gap: 0.25rem;
    margin-bottom: 0.25rem;
  }

  .tiptap-toolbar-group:last-child {
    margin-bottom: 0;
  }

  .tiptap-separator[data-orientation='vertical'] {
    height: 1.25rem;
    display: none;
  }

  /* 工具栏滚动条样式 */
  .tiptap-toolbar[data-variant='fixed']::-webkit-scrollbar {
    width: 4px;
  }

  .tiptap-toolbar[data-variant='fixed']::-webkit-scrollbar-track {
    background: transparent;
  }

  .tiptap-toolbar[data-variant='fixed']::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 2px;
  }

  .tiptap-toolbar[data-variant='fixed']::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3);
  }

  /* 编辑器内容区域底部留出工具栏空间（支持多行工具栏） */
  .simple-editor-content {
    padding-bottom: calc(var(--tt-toolbar-height) * 3 + var(--tt-safe-area-bottom) + 2rem);
  }

  .simple-editor-content .tiptap.ProseMirror {
    padding-bottom: 1rem;
  }
}

@media screen and (max-width: 480px) {
  .el-dialog {
    width: 95% !important;
    margin: 2vh auto;
  }

  .el-dialog__body {
    padding: 12px;
  }

  .el-upload-dragger {
    height: 120px;
  }

  .el-upload__text {
    font-size: 12px;
  }

  /* 更小的工具栏按钮 */
  .tiptap-button {
    height: 1.75rem;
    min-width: 1.75rem;
    padding: 0.375rem;
  }

  .tiptap-button .tiptap-button-icon {
    width: 0.875rem;
    height: 0.875rem;
  }

  /* 工具栏进一步优化 */
  .tiptap-toolbar[data-variant='fixed'] {
    padding: 0.375rem 0.375rem calc(var(--tt-safe-area-bottom) + 0.375rem);
    max-height: calc(var(--tt-toolbar-height) * 4 + var(--tt-safe-area-bottom) + 1rem);
  }

  .tiptap-toolbar-group {
    gap: 0.125rem;
    margin-bottom: 0.125rem;
  }

  /* 编辑器内容区域调整 */
  .simple-editor-content {
    padding-bottom: calc(var(--tt-toolbar-height) * 4 + var(--tt-safe-area-bottom) + 1.5rem);
  }
}
</style>
