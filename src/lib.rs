//! # Envision GPU Core Engine Roadmap
//!
//! This crate powers the Envision editor's GPU subsystem, providing a persistent WGPU-based
//! rendering core with a Python scripting interface. The long-term goal is to support a
//! layer-based composition workflow, real-time effect evaluation, and tight integration between
//! Rust-native GPU processing and Python-driven tools, similar to professional motion graphics
//! suites like Adobe After Effects.

mod gpu_core;
pub mod texture_manager;

use std::sync::Mutex;

use gpu_core::{EffectCommand, EffectParameters, GpuCore, LayerCommand, RenderParams};
use once_cell::sync::Lazy;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::FromPyObject;

static GPU_CORE: Lazy<Mutex<Option<GpuCore>>> = Lazy::new(|| Mutex::new(None));

#[derive(FromPyObject)]
struct EffectDescriptor {
    effect_id: String,
    #[pyo3(default)]
    intensity: Option<f32>,
    #[pyo3(default)]
    blend: Option<f32>,
}

#[derive(FromPyObject)]
struct LayerDescriptor {
    layer_id: String,
    #[pyo3(default)]
    effects: Vec<EffectDescriptor>,
}

fn with_gpu_core<F, R>(f: F) -> PyResult<R>
where
    F: FnOnce(&mut GpuCore) -> anyhow::Result<R>,
{
    let mut guard = GPU_CORE
        .lock()
        .map_err(|_| PyRuntimeError::new_err("GPU core mutex poisoned"))?;

    if guard.is_none() {
        let core = GpuCore::initialize().map_err(|err| PyRuntimeError::new_err(err.to_string()))?;
        *guard = Some(core);
    }

    let core = guard.as_mut().expect("GPU core must be initialized");
    f(core).map_err(|err| PyRuntimeError::new_err(err.to_string()))
}

#[pyfunction]
fn initialize() -> PyResult<()> {
    with_gpu_core(|_| Ok(()))
}

#[pyfunction]
fn render_frame(
    target_label: Option<String>,
    width: Option<u32>,
    height: Option<u32>,
    time: Option<f32>,
    layers: Option<Vec<LayerDescriptor>>,
) -> PyResult<()> {
    let params = RenderParams {
        target_label: target_label.unwrap_or_else(|| "framebuffer".to_string()),
        width: width.unwrap_or(1920),
        height: height.unwrap_or(1080),
        time: time.unwrap_or(0.0),
        layers: layers
            .unwrap_or_default()
            .into_iter()
            .map(|layer| LayerCommand {
                layer_id: layer.layer_id,
                effect_stack: layer
                    .effects
                    .into_iter()
                    .map(|effect| EffectCommand {
                        effect_id: effect.effect_id,
                        parameters: EffectParameters {
                            intensity: effect.intensity.unwrap_or(1.0),
                            blend: effect.blend.unwrap_or(1.0),
                        },
                    })
                    .collect(),
            })
            .collect(),
    };

    with_gpu_core(|core| core.render_frame(params))
}

#[pyfunction]
fn apply_filter_to_texture(
    target_label: String,
    effect_id: String,
    intensity: Option<f32>,
    blend: Option<f32>,
) -> PyResult<()> {
    let layer_command = LayerCommand {
        layer_id: "single-layer".to_string(),
        effect_stack: vec![EffectCommand {
            effect_id,
            parameters: EffectParameters {
                intensity: intensity.unwrap_or(1.0),
                blend: blend.unwrap_or(1.0),
            },
        }],
    };

    let params = RenderParams {
        target_label,
        layers: vec![layer_command],
        ..RenderParams::default()
    };

    with_gpu_core(|core| core.render_frame(params))
}

#[pymodule]
fn envision_gpu_core(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(render_frame, m)?)?;
    m.add_function(wrap_pyfunction!(apply_filter_to_texture, m)?)?;
    Ok(())
}
