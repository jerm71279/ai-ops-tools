import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
    );

    const { syncConfigId, accessToken } = await req.json();

    console.log("Starting SharePoint sync for config:", syncConfigId);

    // Get sync configuration
    const { data: syncConfig, error: configError } = await supabaseClient
      .from("sharepoint_sync_config")
      .select("*")
      .eq("id", syncConfigId)
      .single();

    if (configError || !syncConfig) {
      throw new Error(`Failed to get sync config: ${configError?.message}`);
    }

    // Create sync log entry
    const { data: syncLog, error: logError } = await supabaseClient
      .from("sharepoint_sync_logs")
      .insert({
        sync_config_id: syncConfigId,
        status: "running",
      })
      .select()
      .single();

    if (logError) {
      throw new Error(`Failed to create sync log: ${logError.message}`);
    }

    let filesSynced = 0;
    let filesFailed = 0;
    const syncDetails: any = {
      files: [],
      errors: [],
    };

    try {
      // Build Graph API URL for SharePoint files
      const libraryPath = syncConfig.library_id
        ? `/drives/${syncConfig.library_id}/root/children`
        : `/sites/${syncConfig.site_id}/drive/root/children`;
      
      const graphUrl = `https://graph.microsoft.com/v1.0${libraryPath}`;

      console.log("Fetching files from:", graphUrl);

      // Fetch files from SharePoint
      const filesResponse = await fetch(graphUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!filesResponse.ok) {
        const errorText = await filesResponse.text();
        throw new Error(`Graph API error: ${filesResponse.status} ${errorText}`);
      }

      const filesData = await filesResponse.json();
      const files = filesData.value || [];

      console.log(`Found ${files.length} files in SharePoint`);

      // Filter files by extension if configured
      const filteredFiles = syncConfig.filter_extensions?.length
        ? files.filter((file: any) => {
            const ext = file.name.split(".").pop()?.toLowerCase();
            return syncConfig.filter_extensions.includes(ext);
          })
        : files;

      console.log(`Processing ${filteredFiles.length} files after filtering`);

      // Process each file
      for (const file of filteredFiles) {
        try {
          // Skip folders
          if (file.folder) {
            continue;
          }

          // Check if file already exists in knowledge base
          const { data: existingFile } = await supabaseClient
            .from("knowledge_files")
            .select("id")
            .eq("storage_path", `sharepoint:${file.id}`)
            .maybeSingle();

          if (existingFile) {
            console.log(`File already synced: ${file.name}`);
            syncDetails.files.push({
              name: file.name,
              status: "skipped",
              reason: "already_exists",
            });
            continue;
          }

          // Download file content
          const downloadUrl = file["@microsoft.graph.downloadUrl"];
          const fileContentResponse = await fetch(downloadUrl);
          
          if (!fileContentResponse.ok) {
            throw new Error(`Failed to download file: ${file.name}`);
          }

          const fileContent = await fileContentResponse.blob();
          const fileSize = file.size;

          // Create knowledge file entry
          const { data: knowledgeFile, error: fileError } = await supabaseClient
            .from("knowledge_files")
            .insert({
              customer_id: syncConfig.customer_id,
              file_name: file.name,
              file_type: file.name.split(".").pop()?.toLowerCase() || "unknown",
              file_size: fileSize,
              storage_path: `sharepoint:${file.id}`,
              uploaded_by: "00000000-0000-0000-0000-000000000000", // System user
              metadata: {
                sharepoint_id: file.id,
                sharepoint_url: file.webUrl,
                site_id: syncConfig.site_id,
                site_name: syncConfig.site_name,
                modified_at: file.lastModifiedDateTime,
                created_at: file.createdDateTime,
              },
              processed_status: "pending",
            })
            .select()
            .single();

          if (fileError) {
            throw new Error(`Failed to create knowledge file: ${fileError.message}`);
          }

          // Trigger knowledge processor (async)
          await supabaseClient.functions.invoke("knowledge-processor", {
            body: {
              action: "process_file",
              file_id: knowledgeFile.id,
            },
          });

          filesSynced++;
          syncDetails.files.push({
            name: file.name,
            status: "synced",
            size: fileSize,
            knowledge_file_id: knowledgeFile.id,
          });

          console.log(`Successfully synced: ${file.name}`);
        } catch (fileError) {
          filesFailed++;
          const errorMsg = fileError instanceof Error ? fileError.message : "Unknown error";
          syncDetails.errors.push({
            file: file.name,
            error: errorMsg,
          });
          console.error(`Error syncing file ${file.name}:`, errorMsg);
        }
      }

      // Update sync log with success
      await supabaseClient
        .from("sharepoint_sync_logs")
        .update({
          sync_completed_at: new Date().toISOString(),
          status: "completed",
          files_synced: filesSynced,
          files_failed: filesFailed,
          sync_details: syncDetails,
        })
        .eq("id", syncLog.id);

      // Update last sync time on config
      await supabaseClient
        .from("sharepoint_sync_config")
        .update({
          last_sync_at: new Date().toISOString(),
        })
        .eq("id", syncConfigId);

      return new Response(
        JSON.stringify({
          success: true,
          files_synced: filesSynced,
          files_failed: filesFailed,
          sync_log_id: syncLog.id,
        }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    } catch (syncError) {
      // Update sync log with failure
      await supabaseClient
        .from("sharepoint_sync_logs")
        .update({
          sync_completed_at: new Date().toISOString(),
          status: "failed",
          files_synced: filesSynced,
          files_failed: filesFailed,
          error_message: syncError instanceof Error ? syncError.message : "Unknown error",
          sync_details: syncDetails,
        })
        .eq("id", syncLog.id);

      throw syncError;
    }
  } catch (error) {
    console.error("SharePoint sync error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error occurred",
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
