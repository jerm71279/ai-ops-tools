import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface NinjaOneDevice {
  id: number;
  systemName: string;
  nodeClass: string;
  nodeRoleName: string;
  status: string;
  ipAddresses?: string[];
  macAddresses?: string[];
  os?: {
    name?: string;
    version?: string;
  };
  system?: {
    manufacturer?: string;
    model?: string;
    serialNumber?: string;
  };
  cpu?: {
    name?: string;
  };
  memory?: number;
  lastContact?: string;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      throw new Error('Missing authorization header');
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: authHeader } } }
    );

    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      throw new Error('Unauthorized');
    }

    // Get user's customer_id
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('customer_id')
      .eq('user_id', user.id)
      .single();

    if (!profile?.customer_id) {
      throw new Error('User profile not found');
    }

    const customerId = profile.customer_id;

    // Check for NinjaOne credentials
    const clientId = Deno.env.get('NINJAONE_CLIENT_ID');
    const clientSecret = Deno.env.get('NINJAONE_CLIENT_SECRET');
    const instance = Deno.env.get('NINJAONE_INSTANCE') || 'app';

    if (!clientId || !clientSecret) {
      console.log('NinjaOne credentials not configured, using mock data');
      
      // Return mock sync results
      return new Response(
        JSON.stringify({
          success: true,
          message: 'Mock sync completed - Please configure NinjaOne credentials (NINJAONE_CLIENT_ID, NINJAONE_CLIENT_SECRET, NINJAONE_INSTANCE)',
          stats: {
            devicesProcessed: 5,
            devicesCreated: 5,
            devicesUpdated: 0,
            relationshipsCreated: 3,
            errors: 0
          }
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Get OAuth token from NinjaOne
    const tokenResponse = await fetch(`https://${instance}.ninjarmm.com/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: clientId,
        client_secret: clientSecret,
        scope: 'monitoring'
      })
    });

    if (!tokenResponse.ok) {
      throw new Error(`NinjaOne authentication failed: ${tokenResponse.statusText}`);
    }

    const { access_token } = await tokenResponse.json();

    // Fetch devices from NinjaOne
    const devicesResponse = await fetch(`https://${instance}.ninjarmm.com/api/v2/devices`, {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!devicesResponse.ok) {
      throw new Error(`Failed to fetch devices: ${devicesResponse.statusText}`);
    }

    const devices: NinjaOneDevice[] = await devicesResponse.json();
    
    let devicesCreated = 0;
    let devicesUpdated = 0;
    let relationshipsCreated = 0;
    let errors = 0;

    // Process each device
    for (const device of devices) {
      try {
        // Map NinjaOne device to CI
        const ciType = mapDeviceType(device.nodeClass);
        const ciStatus = device.status === 'ONLINE' ? 'active' : 'inactive';
        const criticality = determineCriticality(device);

        // Check if device already exists
        const { data: existingCI } = await supabase
          .from('configuration_items')
          .select('id')
          .eq('ninjaone_device_id', device.id.toString())
          .eq('customer_id', customerId)
          .single();

        const ciData = {
          customer_id: customerId,
          ci_name: device.systemName || `Device-${device.id}`,
          ci_type: ciType,
          ci_status: ciStatus,
          criticality: criticality,
          hostname: device.systemName,
          ip_address: device.ipAddresses?.[0] || null,
          mac_address: device.macAddresses?.[0] || null,
          operating_system: device.os?.name || null,
          version: device.os?.version || null,
          manufacturer: device.system?.manufacturer || null,
          model: device.system?.model || null,
          serial_number: device.system?.serialNumber || null,
          ninjaone_device_id: device.id.toString(),
          integration_source: 'ninjaone',
          created_by: user.id,
          updated_by: user.id,
          attributes: {
            cpu: device.cpu?.name,
            memory_gb: device.memory ? Math.round(device.memory / 1024 / 1024 / 1024) : null,
            last_contact: device.lastContact,
            node_role: device.nodeRoleName
          }
        };

        if (existingCI) {
          // Update existing CI
          const { error: updateError } = await supabase
            .from('configuration_items')
            .update(ciData)
            .eq('id', existingCI.id);

          if (updateError) throw updateError;
          devicesUpdated++;
        } else {
          // Create new CI
          const { error: insertError } = await supabase
            .from('configuration_items')
            .insert(ciData);

          if (insertError) throw insertError;
          devicesCreated++;
        }

      } catch (err) {
        console.error(`Error processing device ${device.id}:`, err);
        errors++;
      }
    }

    // Log the sync activity
    await supabase
      .from('audit_logs')
      .insert({
        customer_id: customerId,
        user_id: user.id,
        system_name: 'cmdb',
        action_type: 'ninjaone_sync',
        action_details: {
          devices_processed: devices.length,
          devices_created: devicesCreated,
          devices_updated: devicesUpdated,
          relationships_created: relationshipsCreated,
          errors: errors
        },
        compliance_tags: ['cmdb', 'integration']
      });

    return new Response(
      JSON.stringify({
        success: true,
        message: `Successfully synced ${devices.length} devices from NinjaOne`,
        stats: {
          devicesProcessed: devices.length,
          devicesCreated,
          devicesUpdated,
          relationshipsCreated,
          errors
        }
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('NinjaOne sync error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(
      JSON.stringify({
        success: false,
        error: errorMessage
      }),
      { 
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});

function mapDeviceType(nodeClass: string): string {
  const mapping: Record<string, string> = {
    'WINDOWS_WORKSTATION': 'hardware',
    'WINDOWS_SERVER': 'hardware',
    'MAC': 'hardware',
    'LINUX_SERVER': 'hardware',
    'LINUX_WORKSTATION': 'hardware',
    'NAS': 'hardware',
    'VM_HOST': 'hardware',
    'VIRTUAL_MACHINE': 'hardware'
  };
  return mapping[nodeClass] || 'hardware';
}

function determineCriticality(device: NinjaOneDevice): string {
  // Servers and VM hosts are high criticality
  if (device.nodeClass?.includes('SERVER') || device.nodeClass?.includes('VM_HOST')) {
    return 'high';
  }
  // Production workstations are medium
  if (device.nodeRoleName?.toLowerCase().includes('production')) {
    return 'medium';
  }
  // Everything else is low by default
  return 'low';
}
