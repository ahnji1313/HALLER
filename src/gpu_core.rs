use anyhow::{anyhow, Result};
use log::debug;
use wgpu::{Adapter, Device, Instance, Queue, RequestAdapterOptions};

use crate::texture_manager::TextureManager;

#[derive(Debug, Clone)]
pub struct RenderParams {
    pub target_label: String,
    pub width: u32,
    pub height: u32,
    pub time: f32,
    pub layers: Vec<LayerCommand>,
}

impl Default for RenderParams {
    fn default() -> Self {
        Self {
            target_label: "framebuffer".to_string(),
            width: 1920,
            height: 1080,
            time: 0.0,
            layers: Vec::new(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct LayerCommand {
    pub layer_id: String,
    pub effect_stack: Vec<EffectCommand>,
}

#[derive(Debug, Clone)]
pub struct EffectCommand {
    pub effect_id: String,
    pub parameters: EffectParameters,
}

#[derive(Debug, Clone, Default)]
pub struct EffectParameters {
    pub intensity: f32,
    pub blend: f32,
}

pub struct GpuCore {
    _instance: Instance,
    _adapter: Adapter,
    device: Device,
    queue: Queue,
    texture_manager: TextureManager,
}

impl GpuCore {
    pub fn initialize() -> Result<Self> {
        pollster::block_on(Self::async_initialize())
    }

    async fn async_initialize() -> Result<Self> {
        let instance = Instance::default();
        let adapter = instance
            .request_adapter(&RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                compatible_surface: None,
                force_fallback_adapter: false,
            })
            .await
            .ok_or_else(|| anyhow!("Failed to find a suitable GPU adapter"))?;

        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    label: Some("envision-gpu-core-device"),

                    features: wgpu::Features::empty(),
                    limits: wgpu::Limits::default(),
                },
                None,
            )
            .await?;

        debug!("GPU device initialized");

        let mut texture_manager = TextureManager::new();
        texture_manager.ensure_texture(
            &device,
            "framebuffer",
            wgpu::Extent3d {
                width: 1920,
                height: 1080,
                depth_or_array_layers: 1,
            },
        )?;

        Ok(Self {
            _instance: instance,
            _adapter: adapter,
            device,
            queue,
            texture_manager,
        })
    }

    pub fn render_frame(&mut self, params: RenderParams) -> Result<()> {
        self.texture_manager.ensure_texture(
            &self.device,
            &params.target_label,
            wgpu::Extent3d {
                width: params.width,
                height: params.height,
                depth_or_array_layers: 1,
            },
        )?;

        for layer in &params.layers {
            self.process_layer(layer)?;
        }

        // TODO: Encode and submit actual GPU commands to render the frame.
        debug!(
            "Rendered frame for target `{}` at {}x{} with {} layers",
            params.target_label,
            params.width,
            params.height,
            params.layers.len()
        );

        Ok(())
    }

    fn process_layer(&mut self, layer: &LayerCommand) -> Result<()> {
        for effect in &layer.effect_stack {
            self.apply_effect(layer, effect)?;
        }
        Ok(())
    }

    fn apply_effect(&mut self, layer: &LayerCommand, effect: &EffectCommand) -> Result<()> {
        // TODO: Encode effect-specific GPU pipelines and dispatches.
        debug!(
            "Applying effect `{}` to layer `{}` with intensity {} and blend {}",
            effect.effect_id,
            layer.layer_id,
            effect.parameters.intensity,
            effect.parameters.blend
        );
        Ok(())
    }

    pub fn device(&self) -> &Device {
        &self.device
    }

    pub fn queue(&self) -> &Queue {
        &self.queue
    }
}
