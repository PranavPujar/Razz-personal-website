import ThreeGlobe from "three-globe";
import { WebGLRenderer, Scene, Color, Fog, PerspectiveCamera, AmbientLight, DirectionalLight, PointLight } from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import countries from "./files/globe-data-min.json";
import travelHistory from "./files/my-flights.json";
import airportHistory from "./files/my-airports.json";
import Lenis from 'lenis';

var renderer, camera, scene, controls, lenis;
var Globe;

init();
initGlobe();
onWindowResize();
animate();

setTimeout(() => {
  document.body.classList.add('hero-exited');
  document.getElementById('main-nav').classList.add('visible');
  
  // Re-size renderer for globe now that container is visible
  setTimeout(onWindowResize, 10);
  
  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true
  });

  function raf(time) {
    if (lenis) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
  }
  requestAnimationFrame(raf);
}, 100);

function init() {
  renderer = new WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  
  // Important: Set size for the globe container
  const container = document.getElementById("globe-container");
  if (container) {
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
  }

  scene = new Scene();
  scene.add(new AmbientLight(0xbbbbbb, 0.3));
  renderer.setClearColor(0x000000, 0);

  camera = new PerspectiveCamera();
  camera.aspect = container ? container.clientWidth / container.clientHeight : window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  var dLight = new DirectionalLight(0xffffff, 0.8);
  dLight.position.set(-800, 2000, 400);
  camera.add(dLight);

  var dLight1 = new DirectionalLight(0x7982f6, 1);
  dLight1.position.set(-200, 500, 200);
  camera.add(dLight1);

  camera.position.z = 400;
  scene.add(camera);
  scene.fog = new Fog(0x535ef3, 400, 2000);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enableZoom = false;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.5;

  window.addEventListener("resize", onWindowResize, false);
  
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("light-mode");
      updateGlobeMaterial();
    });
  }

  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      if (link.getAttribute('target') === '_blank') return;
      e.preventDefault();
      const targetView = link.getAttribute('data-view');
      document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
      document.getElementById(`view-${targetView}`).classList.add('active');
      if (lenis) lenis.scrollTo(0);
    });
  });
  
}

function updateGlobeMaterial() {
  if (!Globe) return;
  const isLight = document.body.classList.contains("light-mode");
  const globeMaterial = Globe.globeMaterial();
  if (isLight) {
    globeMaterial.color = new Color(0xcccccc);
    globeMaterial.emissive = new Color(0x444444);
    globeMaterial.emissiveIntensity = 0.2;
    Globe.hexPolygonColor(() => "rgba(0,0,0, 0.7)");
  } else {
    globeMaterial.color = new Color(0xffffff);
    globeMaterial.emissive = new Color(0x220038);
    globeMaterial.emissiveIntensity = 0.1;
    Globe.hexPolygonColor(() => "rgba(255,255,255, 0.7)");
  }
}

function initGlobe() {
  Globe = new ThreeGlobe({ waitForGlobeReady: true, animateIn: true })
    .hexPolygonsData(countries.features)
    .hexPolygonResolution(3)
    .hexPolygonMargin(0.7)
    .showAtmosphere(true)
    .atmosphereColor("#3a228a")
    .atmosphereAltitude(0.25)
    .hexPolygonColor(() => "rgba(255,255,255, 0.7)");

  setTimeout(() => {
    Globe.arcsData(travelHistory.flights)
      .arcColor(e => e.status ? "#9cff00" : "#FF4000")
      .arcAltitude(e => e.arcAlt)
      .arcStroke(e => e.status ? 0.5 : 0.3)
      .arcDashLength(0.9)
      .arcDashGap(4)
      .arcDashAnimateTime(1000)
      .arcsTransitionDuration(1000)
      .labelsData(airportHistory.airports)
      .labelColor(() => "#ffcb21")
      .labelText("city")
      .labelSize(2)
      .pointsData(airportHistory.airports)
      .pointColor(() => "#ffffff")
      .pointRadius(0.05);
  }, 1000);

  Globe.rotateY(-Math.PI * (5 / 9));
  Globe.rotateZ(-Math.PI / 6);
  updateGlobeMaterial();
  scene.add(Globe);
}

function onWindowResize() {
  const container = document.getElementById("globe-container");
  const width = (container && container.clientWidth > 0) ? container.clientWidth : window.innerWidth;
  const height = (container && container.clientHeight > 0) ? container.clientHeight : window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function animate() {
  camera.lookAt(scene.position);
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
