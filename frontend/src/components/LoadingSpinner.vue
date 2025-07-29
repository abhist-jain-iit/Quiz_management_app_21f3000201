<template>
  <div class="loading-container" :class="{ overlay: overlay }">
    <div class="loading-content">
      <div class="spinner-border" :class="spinnerClass" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <div v-if="message" class="loading-message mt-3">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoadingSpinner",
  props: {
    overlay: {
      type: Boolean,
      default: false,
    },
    message: {
      type: String,
      default: "",
    },
    size: {
      type: String,
      default: "normal",
      validator: (value) => ["small", "normal", "large"].includes(value),
    },
    variant: {
      type: String,
      default: "primary",
      validator: (value) =>
        [
          "primary",
          "secondary",
          "success",
          "danger",
          "warning",
          "info",
          "light",
          "dark",
        ].includes(value),
    },
  },
  computed: {
    spinnerClass() {
      const classes = [`text-${this.variant}`];

      if (this.size === "small") {
        classes.push("spinner-border-sm");
      } else if (this.size === "large") {
        classes.push("spinner-border-lg");
      }

      return classes.join(" ");
    },
  },
};
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-container.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 9999;
  min-height: 100vh;
}

.loading-content {
  text-align: center;
  color: var(--text-color);
}

.overlay .loading-content {
  color: #ffffff;
}

.loading-message {
  font-size: 1.1rem;
  font-weight: 500;
}

.spinner-border-lg {
  width: 3rem;
  height: 3rem;
}

.spinner-border {
  animation: spinner-border 0.75s linear infinite;
}

@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}
</style>
