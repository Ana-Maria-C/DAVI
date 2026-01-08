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
    @Input() searchTerm: string = '';

    @ViewChild('graphContainer') container!: ElementRef;

    private graph: any;

    ngAfterViewInit() {
        this.initGraph();
    }

    ngOnChanges() {
        if (this.graph) {
            // If only searchTerm changed, we might just want to re-render, 
            // but strictly 3d-force-graph usually reacts to graphData change or explicit update.
            // We can trigger a color update:
            this.graph.nodeColor(this.graph.nodeColor());

            // If nodes changed, we update data
            if (this.nodes.length > 0) {
                this.updateGraph();
            }
        }
    }

    initGraph() {
        const elem = this.container.nativeElement;

        this.graph = (ForceGraph3D as any)()(elem)
            .backgroundColor('#1a1d21') // Matches var(--bg-default)
            .nodeLabel('label')
            // .nodeAutoColorBy('group') // Removed to handle colors manually
            .nodeColor((node: any) => this.getNodeColor(node))
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed((d: any) => 0.005)
            .width(elem.offsetWidth)
            .height(elem.offsetHeight);

        if (this.nodes.length > 0) {
            this.updateGraph();
        }
    }

    getNodeColor(node: any): string {
        // 1. Highlight Match
        if (this.searchTerm && this.searchTerm.trim().length > 0) {
            const term = this.searchTerm.toLowerCase();
            const label = (node.label || '').toLowerCase();
            if (label.includes(term)) {
                return '#FFD700'; // Gold/Yellow for match
            }
        }

        // 2. Default Group Colors
        switch (node.group) {
            case 'http://example.org/movielens/Movie':
                return '#4A90E2'; // Blue
            case 'http://example.org/movielens/Genre':
                return '#9013FE'; // Purple
            case 'http://example.org/movielens/Tag':
                return '#50E3C2'; // Teal/Green
            case 'http://example.org/movielens/RatingGroup':
                return '#F5A623'; // Orange
            default:
                return '#9B9B9B'; // Grey
        }
    }

    updateGraph() {
        const gData = {
            nodes: this.nodes.map(n => ({ ...n })), // Clone to avoid mutation issues
            links: this.links.map(l => ({ ...l }))
        };

        this.graph.graphData(gData);
    }

    ngOnDestroy() {
        // Cleanup if necessary (3d-force-graph doesn't have a specific destroy method but we can clear refs)
        this.graph = null;
    }
}
