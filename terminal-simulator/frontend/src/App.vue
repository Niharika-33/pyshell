<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-white font-mono">
    <!-- Header -->
    <header class="bg-gray-800 p-4 border-b border-gray-700">
      <h1 class="text-xl font-bold">Terminal Simulator</h1>
    </header>

    <!-- Main Content -->
    <main class="flex-grow flex flex-col p-4">
      <!-- Terminal Display -->
      <div
        id="terminal"
        class="bg-black rounded-lg p-4 mb-4 flex-grow font-mono text-sm overflow-auto h-96"
      >
        <div v-for="(entry, index) in terminalOutput" :key="index" class="mb-1">
          <span :class="entry.prompt ? 'text-green-400' : ''">{{
            entry.prompt
          }}</span>
          <span
            :class="entry.type === 'error' ? 'text-red-400' : 'text-blue-400'"
            >{{ entry.content }}</span
          >
        </div>
      </div>

      <!-- Input Area -->
      <div class="flex items-center relative">
        <span class="text-green-400 mr-2">{{ currentPrompt }}</span>
        <input
          type="text"
          ref="commandInput"
          v-model="inputCommand"
          @keyup.enter="executeCommand"
          @keyup.up="previousCommand"
          @keyup.down="nextCommand"
          @keydown.tab.prevent="autocomplete"
          @input="getSuggestions"
          class="flex-grow bg-transparent border-none outline-none text-white focus:outline-none"
          placeholder="Enter command..."
          autocomplete="off"
        />
        <!-- Suggestions dropdown -->
        <div
          v-if="suggestions.length > 0 && inputCommand"
          class="absolute left-0 right-0 top-full mt-1 bg-gray-800 rounded-lg shadow-lg z-10 w-full md:w-1/2 lg:w-1/3"
        >
          <button
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="selectSuggestion(suggestion)"
            class="block w-full text-left px-4 py-2 text-white hover:bg-gray-700 focus:outline-none"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer
      class="bg-gray-800 p-2 text-center text-xs text-gray-400 border-t border-gray-700"
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
        this.inputCommand = this.suggestions[0] + " ";
        this.suggestions = [];
      }
    },

    selectSuggestion(suggestion) {
      this.inputCommand = suggestion + " ";
      this.suggestions = [];
      this.$refs.commandInput.focus();
    },
  },
  mounted() {
    // Focus input on mount
    this.$refs.commandInput.focus();
  },
};
</script>

<style scoped>
/* You can add any custom styles here */
</style>
