<template>
  <div
    class="min-h-screen flex flex-col font-mono transition-colors duration-300"
    :class="{
      'bg-gray-950 text-white': isDarkMode,
      'bg-gray-100 text-gray-900': !isDarkMode,
    }"
  >
    <!-- Header -->
    <header
      class="p-4 border-b transition-colors duration-300 flex justify-between items-center"
      :class="{
        'bg-gray-800 border-gray-700': isDarkMode,
        'bg-gray-200 border-gray-300': !isDarkMode,
      }"
    >
      <h1 class="text-xl font-bold">Terminal Simulator</h1>
      <button
        @click="toggleTheme"
        class="p-2 rounded-full transition-colors duration-300"
        :class="{
          'bg-gray-700 text-white hover:bg-gray-600': isDarkMode,
          'bg-gray-300 text-gray-800 hover:bg-gray-400': !isDarkMode,
        }"
      >
        <svg
          v-if="isDarkMode"
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
          />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      </button>
    </header>

    <!-- Main Content -->
    <main class="flex-grow flex flex-col p-4">
      <!-- Terminal Display -->
      <div
        id="terminal"
        class="rounded-lg p-4 mb-4 flex-grow text-sm overflow-auto h-96 shadow-inner"
        :class="{
          'bg-gray-900 shadow-gray-800': isDarkMode,
          'bg-gray-200 shadow-gray-300': !isDarkMode,
        }"
      >
        <div v-for="(entry, index) in terminalOutput" :key="index" class="mb-1">
          <span
            :class="{
              'text-purple-400': entry.type === 'command',
              'text-green-400': isDarkMode && entry.prompt,
              'text-blue-600': !isDarkMode && entry.prompt,
            }"
            >{{ entry.prompt }}</span
          >
          <span
            :class="{
              'text-red-400': entry.type === 'error' && isDarkMode,
              'text-red-600': entry.type === 'error' && !isDarkMode,
              'text-gray-200': entry.type === 'output' && isDarkMode,
              'text-gray-800': entry.type === 'output' && !isDarkMode,
              'text-blue-400': entry.type === 'info' && isDarkMode,
              'text-blue-600': entry.type === 'info' && !isDarkMode,
            }"
            >{{ entry.content }}</span
          >
        </div>
      </div>

      <!-- Input Area -->
      <div class="flex items-center relative">
        <span
          class="mr-2"
          :class="{
            'text-green-400': isDarkMode,
            'text-blue-600': !isDarkMode,
          }"
          >{{ currentPrompt }}</span
        >
        <input
          type="text"
          ref="commandInput"
          v-model="inputCommand"
          @keyup.enter="executeCommand"
          @keyup.up="previousCommand"
          @keyup.down="nextCommand"
          @keydown.tab.prevent="autocomplete"
          @input="getSuggestions"
          class="flex-grow bg-transparent border-none outline-none focus:outline-none placeholder-gray-500"
          :class="{ 'text-white': isDarkMode, 'text-gray-900': !isDarkMode }"
          placeholder="Enter command..."
          autocomplete="off"
        />
        <!-- Suggestions dropdown -->
        <div
          v-if="suggestions.length > 0 && inputCommand"
          class="absolute left-0 right-0 top-full mt-1 rounded-lg shadow-lg z-10 w-full md:w-1/2 lg:w-1/3"
          :class="{ 'bg-gray-800': isDarkMode, 'bg-gray-200': !isDarkMode }"
        >
          <button
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="selectSuggestion(suggestion)"
            class="block w-full text-left px-4 py-2 transition-colors duration-200"
            :class="{
              'text-white hover:bg-gray-700 focus:bg-gray-700': isDarkMode,
              'text-gray-900 hover:bg-gray-300 focus:bg-gray-300': !isDarkMode,
            }"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer
      class="p-2 text-center text-xs border-t transition-colors duration-300"
      :class="{
        'bg-gray-800 text-gray-400 border-gray-700': isDarkMode,
        'bg-gray-200 text-gray-600 border-gray-300': !isDarkMode,
      }"
    >
      Terminal Simulator v1.0
    </footer>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      inputCommand: "",
      terminalOutput: [
        {
          prompt: "user@terminal:~$ ",
          content: "Welcome to Terminal Simulator",
          type: "info",
        },
        {
          prompt: "user@terminal:~$ ",
          content: "Type 'help' for available commands",
          type: "info",
        },
      ],
      commandHistory: [],
      historyIndex: -1,
      currentPrompt: "user@terminal:~$ ",
      suggestions: [],
      isDarkMode: true, // Default to dark mode
    };
  },
  methods: {
    async executeCommand() {
      const command = this.inputCommand.trim();
      if (!command) return;

      // Add command to output
      this.terminalOutput.push({
        prompt: this.currentPrompt,
        content: command,
        type: "command",
      });

      // Add to history
      this.commandHistory.push(command);
      this.historyIndex = -1;
      this.suggestions = [];

      try {
        // Send command to backend
        const response = await axios.post("/execute", { command });
        const { output, error } = response.data;

        // Add output to terminal
        if (output) {
          const lines = output.split("\n").filter((line) => line.trim() !== "");
          lines.forEach((line) => {
            this.terminalOutput.push({
              prompt: "",
              content: line,
              type: "output",
            });
          });
        }

        if (error) {
          this.terminalOutput.push({
            prompt: "",
            content: error,
            type: "error",
          });
        }

        // Special handling for clear command
        if (command === "clear") {
          this.terminalOutput = [];
        }
      } catch (err) {
        this.terminalOutput.push({
          prompt: "",
          content: "Error communicating with terminal backend",
          type: "error",
        });
      }

      // Clear input
      this.inputCommand = "";

      // Scroll to bottom
      this.$nextTick(() => {
        const terminal = document.getElementById("terminal");
        if (terminal) {
          terminal.scrollTop = terminal.scrollHeight;
        }
      });
    },

    previousCommand() {
      if (this.commandHistory.length === 0) return;

      if (this.historyIndex === -1) {
        this.historyIndex = this.commandHistory.length - 1;
      } else if (this.historyIndex > 0) {
        this.historyIndex--;
      }

      if (this.historyIndex >= 0) {
        this.inputCommand = this.commandHistory[this.historyIndex];
      }
    },

    nextCommand() {
      if (this.historyIndex === -1 || this.commandHistory.length === 0) return;

      if (this.historyIndex < this.commandHistory.length - 1) {
        this.historyIndex++;
        this.inputCommand = this.commandHistory[this.historyIndex];
      } else {
        this.historyIndex = -1;
        this.inputCommand = "";
      }
    },

    async getSuggestions() {
      const partial = this.inputCommand.trim();
      if (partial.length === 0) {
        this.suggestions = [];
        return;
      }

      try {
        const response = await axios.post("/suggestions", { partial });
        this.suggestions = response.data.suggestions;
      } catch (err) {
        this.suggestions = [];
      }
    },

    autocomplete() {
      if (this.suggestions.length > 0) {
        this.inputCommand = this.suggestions[0];
        this.suggestions = [];
      }
    },

    selectSuggestion(suggestion) {
      this.inputCommand = suggestion;
      this.suggestions = [];
      this.$refs.commandInput.focus();
    },

    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
    },
  },
  mounted() {
    // Focus input on mount
    this.$refs.commandInput.focus();
  },
};
</script>

<style scoped>
/* Blinking cursor effect */
input:focus {
  caret-color: transparent;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  from,
  to {
    caret-color: transparent;
  }
  50% {
    caret-color: currentColor;
  }
}
</style>
