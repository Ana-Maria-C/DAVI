import { Component, ElementRef, Input, OnChanges, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
// Force rebuild
import ForceGraph3D from '3d-force-graph';

@Component({
    standalone: false,
    selector: 'app-network-graph',
    template: '<div #graphContainer class="graph-container"></div>',
    styles: [`
    .graph-container {
      width: 100%;
      height: 600px;
      background: #111; /* Fallback/Loading background */
      border-radius: 8px;
      overflow: hidden;
    }
  `]
})
export class NetworkGraphComponent implements OnChanges, AfterViewInit, OnDestroy {
    @Input() nodes: any[] = [];
    @Input() links: any[] = [];

    @ViewChild('graphContainer') container!: ElementRef;

    private graph: any;

    ngAfterViewInit() {
        this.initGraph();
    }

    ngOnChanges() {
        if (this.graph && this.nodes.length > 0) {
            this.updateGraph();
        }
    }

    initGraph() {
        const elem = this.container.nativeElement;

        this.graph = (ForceGraph3D as any)()(elem)
            .backgroundColor('#1a1d21') // Matches var(--bg-default) or --bg-dark-900 roughly
            .nodeLabel('label')
            .nodeAutoColorBy('group')
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed((d: any) => 0.005)
            .width(elem.offsetWidth)
            .height(elem.offsetHeight);

        // Initial Resize Observer to handle container sizing
        // Note: In a real app we might want to attach a ResizeObserver to the container
        // to dynamically update graph.width() and graph.height()

        if (this.nodes.length > 0) {
            this.updateGraph();
        }
    }

    updateGraph() {
        const gData = {
            nodes: this.nodes.map(n => ({ id: n.id, label: n.label, group: n.group })),
            links: this.links.map(l => ({ source: l.source, target: l.target }))
        };

        this.graph.graphData(gData);
    }

    ngOnDestroy() {
        // Cleanup if necessary (3d-force-graph doesn't have a specific destroy method but we can clear refs)
        this.graph = null;
    }
}
