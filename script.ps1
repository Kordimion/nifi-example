# getting the root process id
$nifiurl = "http://localhost:8082"
$rootProcessGroupsResponce = Invoke-RestMethod -Uri "$nifiurl/nifi-api/flow/process-groups/root"
$processGroupId = $rootProcessGroupsResponce.processGroupFlow.id

# uploading the template
$templateFilePath = "D:/code/nifi/filecloner.xml"
$templateName = "filecloner"
$templateBytes = [System.IO.File]::ReadAllBytes($templateFilePath)

$uri = "$nifiUrl/process-groups/$rootProcessGroupId/templates/upload"

$uploadRes = Invoke-RestMethod -Uri $uri -Method POST -Form @{
    file = $templateBytes
}

Write-Host $uploadRes

#$body = @{
    #template = @{
        #name = $templateName
        #snippet = @{
            #encodedValue = $templateBase64
        #}
    #}
#} | ConvertTo-Json
#
#$uploadTemplateResponse = Invoke-RestMethod -Uri "$nifiUrl/process-groups/$rootProcessGroupId/templates/upload" -Method Post -Body $body -ContentType "application/json"
#
#Write-Response $uploadTemplateResponse
#
#$newProcessGroupName = "FileCloner Process Group"
#
##$body = @{
    #revision = @{
        #version = 0
        #clientId = "PowerShell"
    #}
    #component = @{
        #type = "PROCESS_GROUP"
        #name = $newProcessGroupName
        #templateId = $templateName
        #position = @{
            #x = 0
            #y = 0
        #}
    #}
#} | ConvertTo-Json
#
#$newProcessGroup = Invoke-RestMethod -Uri "$nifiUrl/process-groups/$rootProcessGroupId/process-groups" -Method Post -Body $body -ContentType "application/json"
#$newProcessGroupId = $newProcessGroup.id
#
#Write-Host $newProcessGroup
#
## running newly created process group
#
#$body = @{
    #id = $newProcessGroupId
    #state = "RUNNING"
#} | ConvertTo-Json
#
#Invoke-RestMethod -Uri "$nifiUrl/flow/process-groups/$newProcessGroupId" -Method Put -Body $body -ContentType "application/json"
