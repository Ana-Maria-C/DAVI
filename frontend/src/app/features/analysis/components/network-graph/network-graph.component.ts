import { Component, ElementRef, Input, OnChanges, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
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

    private matchedNodeIds = new Set<string>();
    private neighborNodeIds = new Set<string>();
    private highlightedLinkIds = new Set<string>();

    ngAfterViewInit() {
        this.initGraph();
    }

    ngOnChanges() {
        if (this.graph) {
            this.computeHighlights();

            this.graph.nodeColor(this.graph.nodeColor());
            this.graph.linkColor(this.graph.linkColor());
            this.graph.linkWidth(this.graph.linkWidth());
            this.graph.linkDirectionalParticles(this.graph.linkDirectionalParticles());

            if (this.nodes.length > 0 && this.graph.graphData().nodes.length === 0) {
                this.updateGraph();
            } else if (this.nodes.length !== this.graph.graphData().nodes.length) {
                this.updateGraph();
            }
        }
    }

    computeHighlights() {
        this.matchedNodeIds.clear();
        this.neighborNodeIds.clear();
        this.highlightedLinkIds.clear();

        if (!this.searchTerm || this.searchTerm.trim().length === 0) {
            return;
        }

        const term = this.searchTerm.toLowerCase();

        this.nodes.forEach(node => {
            const label = (node.label || '').toLowerCase();
            if (label.includes(term)) {
                this.matchedNodeIds.add(node.id);
            }
        });

        this.links.forEach(link => {
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;

            const isSourceMatch = this.matchedNodeIds.has(sourceId);
            const isTargetMatch = this.matchedNodeIds.has(targetId);

            if (isSourceMatch || isTargetMatch) {
                this.highlightedLinkIds.add(link.id || `${sourceId}-${targetId}`);
                if (isSourceMatch) this.neighborNodeIds.add(targetId);
                if (isTargetMatch) this.neighborNodeIds.add(sourceId);
            }
        });
    }

    initGraph() {
        const elem = this.container.nativeElement;

        this.graph = (ForceGraph3D as any)()(elem)
            .backgroundColor('#1a1d21')
            .nodeLabel('label')

            .nodeColor((node: any) => this.getNodeColor(node))

            .linkColor((link: any) => this.getLinkColor(link))
            .linkWidth((link: any) => this.isHighlightedLink(link) ? 2 : 0.5)

            .linkDirectionalParticles((link: any) => this.isHighlightedLink(link) ? 4 : 0)
            .linkDirectionalParticleSpeed(0.005)
            .linkDirectionalParticleWidth(2)

            .width(elem.offsetWidth)
            .height(elem.offsetHeight);

        if (this.nodes.length > 0) {
            this.updateGraph();
        }
    }

    isHighlightedLink(link: any): boolean {
        if (this.highlightedLinkIds.size === 0) return false;

        const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
        const targetId = typeof link.target === 'object' ? link.target.id : link.target;

        return this.highlightedLinkIds.has(link.id) ||
            this.highlightedLinkIds.has(`${sourceId}-${targetId}`);
    }

    getNodeColor(node: any): string {
        const isSearchActive = this.matchedNodeIds.size > 0;

        if (isSearchActive) {
            if (this.matchedNodeIds.has(node.id)) {
                return '#FFD700';
            } else if (this.neighborNodeIds.has(node.id)) {
                return '#FF4500';
            } else {
                return 'rgba(200, 200, 200, 0.1)';
            }
        }

        switch (node.group) {
            case 'http://example.org/movielens/Movie': return '#4A90E2';
            case 'http://example.org/movielens/Genre': return '#9013FE';
            case 'http://example.org/movielens/Tag': return '#50E3C2';
            case 'http://example.org/movielens/RatingGroup': return '#F5A623';
            default: return '#9B9B9B';
        }
    }

    getLinkColor(link: any): string {
        if (this.matchedNodeIds.size > 0) {
            if (this.isHighlightedLink(link)) {
                return '#FFFFFF';
            } else {
                return 'rgba(255, 255, 255, 0.05)';
            }
        }
        return 'rgba(255, 255, 255, 0.6)';
    }

    updateGraph() {
        const gData = {
            nodes: this.nodes.map(n => ({ ...n })),
            links: this.links.map(l => ({ ...l }))
        };

        this.graph.graphData(gData);

        this.computeHighlights();
    }

    ngOnDestroy() {
        this.graph = null;
    }
}
