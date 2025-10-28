import VanillaTilt from 'vanilla-tilt';

export default {
  name: 'RenderInformationBlockMain',
  mounted() {
    this.initTilt();
    this.initParallax();
  },
  beforeUnmount() {
    this.removeEventListeners();
  },
  methods: {
    initTilt() {
      VanillaTilt.init(document.querySelectorAll(".card-continent-block"), {
        max: 10,
        speed: 400,
        glare: true,
        "max-glare": 0.2,
        scale: 1.05
      });
    },
    initParallax() {
      this.mouseMoveHandler = this.handleMouseMove.bind(this);
      this.scrollHandler = this.handleScroll.bind(this);
      
      document.addEventListener('mousemove', this.mouseMoveHandler);
      window.addEventListener('scroll', this.scrollHandler);
    },
    removeEventListeners() {
      if (this.mouseMoveHandler) {
        document.removeEventListener('mousemove', this.mouseMoveHandler);
      }
      if (this.scrollHandler) {
        window.removeEventListener('scroll', this.scrollHandler);
      }
    },
    handleMouseMove(e) {
      const parallaxBg = document.querySelector('.parallax-bg');
      if (parallaxBg) {
        const x = (window.innerWidth - e.pageX * 2) / 100;
        const y = (window.innerHeight - e.pageY * 2) / 100;
        parallaxBg.style.transform = `translate3d(${x}px, ${y}px, 0) scale(1.1)`;
      }
    },
    handleScroll() {
      const scrolled = window.pageYOffset;
      const parallaxBg = document.querySelector('.parallax-bg');
      if (parallaxBg) {
        const rate = scrolled * -0.5;
        parallaxBg.style.transform = `translate3d(0, ${rate}px, 0) scale(1.1)`;
      }
    }
  }
}