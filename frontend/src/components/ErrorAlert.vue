<template>
  <div 
    v-if="show" 
    class="alert alert-dismissible fade show" 
    :class="alertClass" 
    role="alert"
  >
    <i :class="iconClass" class="me-2"></i>
    <strong v-if="title">{{ title }}:</strong>
    {{ message }}
    <button 
      v-if="dismissible"
      type="button" 
      class="btn-close" 
      @click="dismiss" 
      aria-label="Close"
    ></button>
  </div>
</template>

<script>
export default {
  name: "ErrorAlert",
  props: {
    message: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ""
    },
    variant: {
      type: String,
      default: "danger",
      validator: (value) => ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"].includes(value)
    },
    dismissible: {
      type: Boolean,
      default: true
    },
    show: {
      type: Boolean,
      default: true
    },
    autoHide: {
      type: Boolean,
      default: false
    },
    autoHideDelay: {
      type: Number,
      default: 5000
    }
  },
  emits: ["dismiss"],
  computed: {
    alertClass() {
      return `alert-${this.variant}`;
    },
    iconClass() {
      const iconMap = {
        primary: "bi bi-info-circle-fill",
        secondary: "bi bi-info-circle",
        success: "bi bi-check-circle-fill",
        danger: "bi bi-exclamation-triangle-fill",
        warning: "bi bi-exclamation-triangle-fill",
        info: "bi bi-info-circle-fill",
        light: "bi bi-info-circle",
        dark: "bi bi-info-circle-fill"
      };
      return iconMap[this.variant] || "bi bi-info-circle";
    }
  },
  mounted() {
    if (this.autoHide) {
      setTimeout(() => {
        this.dismiss();
      }, this.autoHideDelay);
    }
  },
  methods: {
    dismiss() {
      this.$emit("dismiss");
    }
  }
};
</script>

<style scoped>
.alert {
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.alert i {
  font-size: 1.1rem;
}

/* Ensure proper contrast */
.alert-danger {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.alert-success {
  background-color: #d1edff;
  border-color: #bee5eb;
  color: #0c5460;
}

.alert-warning {
  background-color: #fff3cd;
  border-color: #ffecb5;
  color: #856404;
}

.alert-info {
  background-color: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}

/* Dark theme adjustments */
@media (prefers-color-scheme: dark) {
  .alert-danger {
    background-color: #2c0b0e;
    border-color: #842029;
    color: #ea868f;
  }

  .alert-success {
    background-color: #051b11;
    border-color: #0f5132;
    color: #75b798;
  }

  .alert-warning {
    background-color: #332701;
    border-color: #997404;
    color: #ffda6a;
  }

  .alert-info {
    background-color: #055160;
    border-color: #087990;
    color: #6edff6;
  }
}
</style>
