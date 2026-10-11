"""Use native Helix embeddings and native Habitus recall in Context Loom."""
from dataclasses import asdict
import numpy as np


class SemanticBridge:
    def __init__(self, encoder):
        self.encoder = encoder
        self.identity = self.space_id = encoder.identity

    def embed(self, text):
        vector = np.asarray(self.encoder.encode_document(text), dtype=float)
        norm = np.linalg.norm(vector)
        if not np.isfinite(vector).all() or norm <= 0:
            raise RuntimeError("Mindscape embedding failed; zero-vector fallback is forbidden")
        return (vector / norm).tolist()


class HabitusLane:
    name = "habitus_graph"

    def __init__(self, mind):
        self.mind = mind
        self.trace = None
        self.paths = ()

    def nominate(self, context):
        from context_loom.retrieval import candidate_for
        result = self.mind.recall(context.query, include_current_input=False)
        self.trace = asdict(result.packet)
        self.paths = self.trace.get("y_paths", ())
        eligible = {record.id: record for record in context.records}
        return [candidate_for(eligible[rid], lane=self.name, score=1.0,
                              reason=f"native Habitus recall: {result.packet.trace_hash}")
                for rid in result.packet.selected_record_ids if rid in eligible]
