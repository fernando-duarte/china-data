// MathJax configuration for China Economic Data Analysis documentation
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    packages: {
      '[+]': ['ams', 'newcommand', 'configmacros']
    }
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  startup: {
    ready: function() {
      MathJax.startup.defaultReady();

      // Custom macros for economic notation
      MathJax.tex.macros = Object.assign(MathJax.tex.macros || {}, {
        // Production function notation
        'Y': '{Y}',
        'K': '{K}',
        'L': '{L}',
        'A': '{A}',
        'alpha': '{\\alpha}',
        'beta': '{\\beta}',
        'gamma': '{\\gamma}',
        'delta': '{\\delta}',

        // Common economic functions
        'prod': ['\\text{#1}', 1],
        'gdp': '\\text{GDP}',
        'tfp': '\\text{TFP}',
        'hc': '\\text{HC}',

        // Mathematical operators
        'diff': '\\mathrm{d}',
        'partial': '\\partial',
        'expect': '\\mathbb{E}',
        'var': '\\text{Var}',
        'cov': '\\text{Cov}',

        // Time notation
        'time': ['_{#1}', 1],
        'growth': ['\\dot{#1}', 1],
        'rate': ['\\hat{#1}', 1]
      });
    }
  },
  svg: {
    fontCache: 'global',
    displayAlign: 'center',
    displayIndent: '0em'
  }
};

// Theme-aware MathJax styling
document.addEventListener('DOMContentLoaded', function() {
  // Function to update MathJax colors based on theme
  function updateMathJaxColors() {
    const isDark = document.querySelector('[data-md-color-scheme="slate"]');
    const mathElements = document.querySelectorAll('.MathJax');

    mathElements.forEach(function(element) {
      if (isDark) {
        element.style.color = '#ffffff';
      } else {
        element.style.color = '#000000';
      }
    });
  }

  // Update colors when theme changes
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'attributes' &&
          mutation.attributeName === 'data-md-color-scheme') {
        setTimeout(updateMathJaxColors, 100);
      }
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });

  // Initial color update
  updateMathJaxColors();
});

// Economic formula examples and common patterns
window.EconomicFormulas = {
  // Cobb-Douglas production function
  cobbDouglas: "Y_t = A_t K_t^{\\alpha} L_t^{1-\\alpha}",

  // Capital accumulation
  capitalAccumulation: "K_{t+1} = (1-\\delta)K_t + I_t",

  // Growth accounting
  growthAccounting: "\\frac{\\dot{Y}}{Y} = \\frac{\\dot{A}}{A} + \\alpha\\frac{\\dot{K}}{K} + (1-\\alpha)\\frac{\\dot{L}}{L}",

  // Solow steady state
  solowSteadyState: "k^* = \\left(\\frac{s}{n+\\delta}\\right)^{\\frac{1}{1-\\alpha}}",

  // Human capital augmented production
  humanCapital: "Y_t = A_t K_t^{\\alpha} (H_t L_t)^{1-\\alpha}"
};

// Helper function to render economic formulas
window.renderFormula = function(formulaKey, elementId) {
  const formula = window.EconomicFormulas[formulaKey];
  if (formula && elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML = '\\[' + formula + '\\]';
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([element]);
      }
    }
  }
};
