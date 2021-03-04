const { H } = window;

const markerSvg =
  '  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="32" height="32" fill="currentColor">' +
  '    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" stroke="#ffffff" stroke-width="1" />' +
  '  </svg>';
const domIconMarkup = `<div class="marker">${markerSvg}</div>`;
const selectedDomIconMarkup = `<div class="marker selected">${markerSvg}</div>`;

export default {
  buildClusterLayer: (data, onClusterClick, onNoiseClick) => {
    const dataPoints = data.map((item) => {
      return new H.clustering.DataPoint(item.lat, item.lng, 1, item);
    });
    const icon = new H.map.DomIcon(domIconMarkup);
    const clusteredDataProvider = new H.clustering.Provider(dataPoints, {
      clusteringOptions: {
        eps: 32,
        minWeight: 3,
      },
    });
    const defaultTheme = clusteredDataProvider.getTheme();
    const customTheme = {
      getClusterPresentation: (cluster) => {
        const clusterMarker = defaultTheme.getClusterPresentation.call(defaultTheme, cluster);
        return clusterMarker;
      },
      getNoisePresentation: (noisePoint) => {
        const noiseMarker = new H.map.DomMarker(noisePoint.getPosition(), {
          icon,
          min: noisePoint.getMinZoom(),
        });
        noiseMarker.setData(noisePoint);
        return noiseMarker;
      },
    };
    clusteredDataProvider.setTheme(customTheme);
    clusteredDataProvider.addEventListener('tap', (event) => {
      if (event.target.getData().getData) {
        onNoiseClick(event.target);
      } else {
        onClusterClick(event.target);
      }
    });
    return new H.map.layer.ObjectLayer(clusteredDataProvider);
  },
  unhighlightMarker: (marker) => {
    const icon = new H.map.DomIcon(domIconMarkup);
    marker.setIcon(icon);
  },
  highlightMarker: (marker) => {
    const selectedIcon = new H.map.DomIcon(selectedDomIconMarkup);
    marker.setIcon(selectedIcon);
  },
};
