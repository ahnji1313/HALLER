use std::collections::HashMap;

use anyhow::{anyhow, Result};
use wgpu::{Device, Extent3d, Texture, TextureDescriptor, TextureDimension, TextureFormat, TextureUsages, TextureView};

#[derive(Debug)]
pub struct TextureHandle {
    pub texture: Texture,
    pub view: TextureView,
    pub size: Extent3d,
}

pub struct TextureManager {
    textures: HashMap<String, TextureHandle>,
}

impl TextureManager {
    pub fn new() -> Self {
        Self {
            textures: HashMap::new(),
        }
    }

    pub fn ensure_texture(&mut self, device: &Device, label: &str, size: Extent3d) -> Result<()> {
        let needs_allocation = match self.textures.get(label) {
            Some(existing) => existing.size != size,
            None => true,
        };

        if needs_allocation {
            let descriptor = TextureDescriptor {
                label: Some(label),
                size,
                mip_level_count: 1,
                sample_count: 1,
                dimension: TextureDimension::D2,
                format: TextureFormat::Rgba8UnormSrgb,
                usage: TextureUsages::TEXTURE_BINDING
                    | TextureUsages::COPY_DST
                    | TextureUsages::STORAGE_BINDING,
                view_formats: &[],
            };

            let texture = device.create_texture(&descriptor);
            let view = texture.create_view(&Default::default());
            let handle = TextureHandle {
                texture,
                view,
                size,
            };
            self.textures.insert(label.to_string(), handle);
        }

        Ok(())
    }

    pub fn get(&self, label: &str) -> Result<&TextureHandle> {
        self.textures
            .get(label)
            .ok_or_else(|| anyhow!("Texture `{}` is not allocated", label))
    }
}
