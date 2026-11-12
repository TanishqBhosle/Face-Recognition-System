import numpy as np
import pytest
from modules.face_recognition import EmbeddingModel

def test_embedding_shape_and_type(mock_face_image):
    """Ensure embedding model returns a 512-element 1D float32 array."""
    model = EmbeddingModel.get_instance()
    embedding = model.generate_embedding(mock_face_image)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (512,)
    assert embedding.dtype == np.float32

def test_embedding_l2_normalization(mock_face_image):
    """Ensure output vector has unit length (L2 norm == 1.0)."""
    model = EmbeddingModel.get_instance()
    embedding = model.generate_embedding(mock_face_image)
    norm = np.linalg.norm(embedding)
    assert np.isclose(norm, 1.0, atol=1e-4)

def test_cosine_distance_identical_vectors():
    """Identical vectors must yield cosine distance of 0.0."""
    v1 = np.random.randn(512).astype(np.float32)
    v1 /= np.linalg.norm(v1)
    
    dist = EmbeddingModel.compute_distance(v1, v1, metric="cosine")
    assert np.isclose(dist, 0.0, atol=1e-5)

def test_cosine_distance_orthogonal_vectors():
    """Orthogonal vectors must yield cosine distance of ~1.0."""
    v1 = np.zeros(512, dtype=np.float32)
    v2 = np.zeros(512, dtype=np.float32)
    v1[0] = 1.0
    v2[1] = 1.0
    
    dist = EmbeddingModel.compute_distance(v1, v2, metric="cosine")
    assert np.isclose(dist, 1.0, atol=1e-5)

def test_empty_face_raises_value_error():
    """Empty or None image input must raise ValueError."""
    model = EmbeddingModel.get_instance()
    with pytest.raises(ValueError):
        model.generate_embedding(np.array([]))

